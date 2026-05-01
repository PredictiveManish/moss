import unittest
from unittest.mock import patch, mock_open, MagicMock

from moss_doc_parser.parsers.pdf import PDFParser
from moss_doc_parser.types import ParseResult


class TestPDFParser(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data=b"%PDF-1.4 test")
    @patch("moss_doc_parser.parsers.pdf.pypdf.PdfReader")
    def test_parse_returns_documents(self, mock_pdf_reader, mock_file):
        # Setup mock for PdfReader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is page text."
        mock_pdf_reader.return_value.pages = [mock_page]

        parser = PDFParser()
        result = parser.parse("dummy_path.pdf")

        # Assertions
        self.assertIsInstance(result, ParseResult)
        self.assertEqual(len(result.documents), 1)
        self.assertEqual(result.documents[0].text, "This is page text.")
        self.assertIn("source_file", result.documents[0].metadata)
        self.assertEqual(result.documents[0].metadata["page_number"], 1)
        self.assertEqual(result.documents[0].metadata["total_pages"], 1)

        # Check that open was called with the right path
        mock_file.assert_called_once_with("dummy_path.pdf", "rb")
        # Check that PdfReader was called with the file handle
        mock_pdf_reader.assert_called_once()
        # Check that extract_text was called on the page
        mock_page.extract_text.assert_called_once()


if __name__ == "__main__":
    unittest.main()
