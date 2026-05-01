"""Markdown document parser."""

import time
from typing import Dict, List

import markdown
from bs4 import BeautifulSoup

from ..base import BaseParser
from ..types import MossDocument, ParseResult


class MarkdownParser(BaseParser):
    """Parser for Markdown files."""

    def __init__(self):
        self.md = markdown.Markdown(extensions=["extra", "toc"])

    def parse(self, file_path: str) -> ParseResult:
        """Parse a Markdown file and extract structured content.

        Args:
            file_path: Path to the Markdown file.

        Returns:
            ParseResult containing structured documents (headers, paragraphs, etc.).
        """
        start_time = time.time()

        with open(file_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Convert markdown to HTML
        self.md.reset()
        html = self.md.convert(markdown_content)

        # Parse HTML with BeautifulSoup for structured extraction
        soup = BeautifulSoup(html, "html.parser")

        documents = []
        current_header = ""
        header_level = 0

        # Process all elements in order
        for element in soup.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "p", "pre", "li"]
        ):
            if element.name.startswith("h"):
                # Header element
                header_level = int(element.name[1])
                current_header = element.get_text().strip()
                if current_header:
                    doc_id = f"{file_path}_header_{len(documents)}"
                    metadata = {
                        "source_file": file_path,
                        "type": "header",
                        "header_level": header_level,
                        "header_text": current_header,
                        "element_index": len(documents),
                    }
                    documents.append(
                        MossDocument(
                            id=doc_id,
                            text=current_header,
                            metadata=metadata,
                        )
                    )
            elif element.name == "p":
                # Paragraph element
                text = element.get_text().strip()
                if text:
                    doc_id = f"{file_path}_para_{len(documents)}"
                    metadata = {
                        "source_file": file_path,
                        "type": "paragraph",
                        "header_context": current_header,
                        "header_level": header_level,
                        "element_index": len(documents),
                    }
                    documents.append(
                        MossDocument(
                            id=doc_id,
                            text=text,
                            metadata=metadata,
                        )
                    )
            elif element.name == "pre":
                # Code block element
                text = element.get_text().strip()
                if text:
                    doc_id = f"{file_path}_code_{len(documents)}"
                    metadata = {
                        "source_file": file_path,
                        "type": "code",
                        "header_context": current_header,
                        "header_level": header_level,
                        "element_index": len(documents),
                    }
                    documents.append(
                        MossDocument(
                            id=doc_id,
                            text=text,
                            metadata=metadata,
                        )
                    )
            elif element.name == "li":
                # List item element
                text = element.get_text().strip()
                if text:
                    doc_id = f"{file_path}_li_{len(documents)}"
                    metadata = {
                        "source_file": file_path,
                        "type": "list_item",
                        "header_context": current_header,
                        "header_level": header_level,
                        "element_index": len(documents),
                    }
                    documents.append(
                        MossDocument(
                            id=doc_id,
                            text=text,
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
        return ["md", "markdown"]
