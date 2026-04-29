"""Load documents from JSON/CSV files, document files, or stdin."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, List

import typer
from moss import DocumentInfo

# Import moss-doc-parser for file parsing
try:
    from moss_doc_parser import FileTypeDetector
    from moss_doc_parser.types import MossDocument
    DOC_PARSER_AVAILABLE = True
except ImportError:
    DOC_PARSER_AVAILABLE = False


def load_documents(file_path: str) -> List[DocumentInfo]:
    """Load documents from a JSON/CSV file, document file, or stdin ('-')."""
    if file_path == "-":
        raw = sys.stdin.read()
        return _parse_json_docs(raw, source="stdin")

    path = Path(file_path)
    if not path.exists():
        raise typer.BadParameter(f"File not found: {file_path}")

    # Check if it's a supported document file for parsing
    suffix = path.suffix.lower()
    if DOC_PARSER_AVAILABLE and suffix in ['.pdf', '.docx', '.pptx', '.html', '.htm', '.md', '.markdown']:
        return _parse_document_file(str(path))
    
    # Otherwise treat as JSON/CSV
    content = path.read_text()
    if suffix == ".csv":
        return _parse_csv_docs(content)
    elif suffix == ".jsonl":
        return _parse_jsonl_docs(content, source=file_path)
    elif suffix == ".json":
        return _parse_json_docs(content, source=file_path)
    else:
        return _parse_json_docs(content, source=file_path)


def _parse_document_file(file_path: str) -> List[DocumentInfo]:
    """Parse a document file using moss-doc-parser and convert to DocumentInfo objects."""
    if not DOC_PARSER_AVAILABLE:
        raise typer.BadParameter(
            f"Document parsing not available. Please install moss-doc-parser to parse {file_path}"
        )
    
    try:
        detector = FileTypeDetector()
        parser = detector.get_parser_for_file(file_path)
        parse_result = parser.parse(file_path)
        
        # Convert MossDocument objects to DocumentInfo objects
        docs = []
        for doc in parse_result.documents:
            docs.append(
                DocumentInfo(
                    id=doc.id,
                    text=doc.text,
                    metadata=doc.metadata,
                )
            )
        return docs
    except Exception as e:
        raise typer.BadParameter(f"Failed to parse document {file_path}: {str(e)}")


def _parse_json_docs(raw: str, source: str = "input") -> List[DocumentInfo]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise typer.BadParameter(f"Invalid JSON in {source}: {e}")

    if isinstance(data, dict):
        data = data.get("documents", data.get("docs", []))

    if not isinstance(data, list):
        raise typer.BadParameter(
            f"Expected a JSON array of documents, got {type(data).__name__}"
        )

    return [_dict_to_doc(d, i) for i, d in enumerate(data)]


def _parse_jsonl_docs(raw: str, source: str = "input") -> List[DocumentInfo]:
    docs = []
    for line_no, line in enumerate(raw.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            raise typer.BadParameter(f"Invalid JSON on line {line_no} in {source}: {e}")
        docs.append(_dict_to_doc(obj, line_no - 1))
    return docs


def _parse_csv_docs(content: str) -> List[DocumentInfo]:
    reader = csv.DictReader(content.splitlines())
    docs = []
    for i, row in enumerate(reader):
        if "id" not in row or "text" not in row:
            raise typer.BadParameter(
                f"CSV row {i + 1}: missing required 'id' or 'text' column"
            )
        metadata = None
        if "metadata" in row and row["metadata"]:
            try:
                metadata = json.loads(row["metadata"])
            except json.JSONDecodeError:
                raise typer.BadParameter(
                    f"CSV row {i + 1}: invalid JSON in 'metadata' column"
                )

        embedding = None
        if "embedding" in row and row["embedding"]:
            try:
                embedding = json.loads(row["embedding"])
            except json.JSONDecodeError:
                raise typer.BadParameter(
                    f"CSV row {i + 1}: invalid JSON in 'embedding' column"
                )

        docs.append(
            DocumentInfo(
                id=row["id"],
                text=row["text"],
                metadata=metadata,
                embedding=embedding,
            )
        )
    return docs


def _dict_to_doc(d: Any, index: int) -> DocumentInfo:
    if not isinstance(d, dict):
        raise typer.BadParameter(f"Document at index {index}: expected object, got {type(d).__name__}")
    if "id" not in d or "text" not in d:
        raise typer.BadParameter(f"Document at index {index}: missing required 'id' or 'text' field")
    return DocumentInfo(
        id=str(d["id"]),
        text=str(d["text"]),
        metadata=d.get("metadata"),
        embedding=d.get("embedding"),
    )
