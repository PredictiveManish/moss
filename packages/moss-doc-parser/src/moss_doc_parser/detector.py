"""File type detector for document parsers."""

from typing import Dict, List, Type

from .base import BaseParser
from .parsers.html import HTMLParser
from .parsers.docx import DocxParser
from .parsers.markdown import MarkdownParser
from .parsers.pdf import PDFParser
from .parsers.pptx import PPTXParser


class FileTypeDetector:
    """Detects file type and returns appropriate parser."""

    def __init__(self):
        self._parsers: Dict[str, Type[BaseParser]] = {
            "pdf": PDFParser,
            "docx": DocxParser,
            "pptx": PPTXParser,
            "html": HTMLParser,
            "htm": HTMLParser,
            "md": MarkdownParser,
            "markdown": MarkdownParser,
        }
        # Try to initialize python-magic, but make it optional
        self._magic_available = False
        self._magic = None
        try:
            import magic
            self._magic = magic.Magic(mime=True)
            self._magic_available = True
        except ImportError:
            pass  # magic not available, we'll rely on extension-based detection

    def get_parser_for_file(self, file_path: str) -> BaseParser:
        """Get the appropriate parser for a file based on its content type.

        Args:
            file_path: Path to the file to analyze.

        Returns:
            An instance of the appropriate parser class.

        Raises:
            ValueError: If no parser is available for the file type.
        """
        # First try extension-based detection
        extension = file_path.lower().split('.')[-1] if '.' in file_path else ''
        if extension in self._parsers:
            return self._parsers[extension]()

        # Fallback to magic byte detection if available
        if self._magic_available:
            try:
                mime_type = self._magic.from_file(file_path)
                mime_to_extension = {
                    "application/pdf": "pdf",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
                    "text/html": "html",
                    "text/plain": "md",  # Assume markdown for plain text
                }
                
                extension = mime_to_extension.get(mime_type)
                if extension and extension in self._parsers:
                    return self._parsers[extension]()
            except Exception:
                pass  # Fall through to extension-based detection failure

        raise ValueError(f"No parser available for file: {file_path}")

    def get_supported_extensions(self) -> List[str]:
        """Get list of all supported file extensions.

        Returns:
            List of supported file extensions (without the dot).
        """
        return list(self._parsers.keys())