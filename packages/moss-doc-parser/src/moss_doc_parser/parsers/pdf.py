"""PDF document parser."""

import time
from typing import Dict, List

import pypdf

from ..base import BaseParser
from ..types import MossDocument, ParseResult


class PDFParser(BaseParser):
    """Parser for PDF files."""

    def parse(self, file_path: str) -> ParseResult:
        """Parse a PDF file and extract text from each page.

        Args:
            file_path: Path to the PDF file.

        Returns:
            ParseResult containing one document per page (or chunked if needed).
        """
        start_time = time.time()

        documents = []
        with open(file_path, "rb") as f:
            pdf = pypdf.PdfReader(f)
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text.strip():  # Only add non-empty pages
                    doc_id = f"{file_path}_page_{page_num}"
                    metadata = {
                        "source_file": file_path,
                        "page_number": page_num + 1,  # 1-indexed for humans
                        "total_pages": len(pdf.pages),
                    }
                    documents.append(
                        MossDocument(
                            id=doc_id,
                            text=text.strip(),
                            metadata=metadata,
                        )
                    )

        parse_time_ms = (time.time() - start_time) * 1000
        return ParseResult(
            documents=documents,
            source_path=file_path,
            parse_time_ms=parse_time_ms,
        )

    def supported_extensions(self) -> List[str]:
        """Return a list of file extensions this parser supports.

        Returns:
            List of file extensions (without the dot).
        """
        return ["pdf"]
