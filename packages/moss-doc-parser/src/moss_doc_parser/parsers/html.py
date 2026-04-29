"""HTML document parser."""

import time
from typing import Dict, List

from bs4 import BeautifulSoup

from ..base import BaseParser
from ..types import MossDocument, ParseResult


class HTMLParser(BaseParser):
    """Parser for HTML files."""

    def parse(self, file_path: str) -> ParseResult:
        """Parse an HTML file and extract text content.

        Args:
            file_path: Path to the HTML file.

        Returns:
            ParseResult containing one document per significant text block.
        """
        start_time = time.time()

        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text and split into meaningful chunks
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_blocks = [chunk for chunk in chunks if chunk]

        documents = []
        for i, text_block in enumerate(text_blocks):
            doc_id = f"{file_path}_block_{i}"
            metadata = {
                "source_file": file_path,
                "block_number": i + 1,  # 1-indexed for humans
                "total_blocks": len(text_blocks),
            }
            documents.append(
                MossDocument(
                    id=doc_id,
                    text=text_block,
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
        return ["html", "htm"]
