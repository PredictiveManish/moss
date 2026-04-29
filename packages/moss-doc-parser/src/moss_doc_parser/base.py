"""Abstract base class for document parsers."""

from abc import ABC, abstractmethod
from typing import List

from .types import ParseResult


class BaseParser(ABC):
    """Abstract base class for all document parsers."""

    @abstractmethod
    def parse(self, file_path: str) -> ParseResult:
        """Parse a file and return a list of MossDocument objects.

        Args:
            file_path: Path to the file to parse.

        Returns:
            ParseResult containing the parsed documents and metadata.
        """
        pass

    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return a list of file extensions this parser supports.

        Returns:
            List of file extensions (without the dot, e.g., ['pdf', 'docx']).
        """
        pass
