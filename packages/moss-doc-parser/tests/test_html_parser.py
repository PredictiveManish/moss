import unittest
from unittest.mock import patch, mock_open, MagicMock

from moss_doc_parser.parsers.html import HTMLParser
from moss_doc_parser.types import ParseResult


class TestHTMLParser(unittest.TestCase):
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="<html><body><h1>Title</h1><p>Paragraph text.</p></body></html>",
    )
    @patch("moss_doc_parser.parsers.html.BeautifulSoup")
    def test_parse_returns_documents(self, mock_bs, mock_file):
        # Setup mock for BeautifulSoup
        mock_soup = MagicMock()
        mock_soup.get_text.return_value = "Title\nParagraph text."
        mock_bs.return_value = mock_soup

        parser = HTMLParser()
        result = parser.parse("dummy_path.html")

        # Assertions
        self.assertIsInstance(result, ParseResult)
        # Should have documents for each text block (title and paragraph)
        self.assertGreaterEqual(len(result.documents), 1)
        self.assertIn("source_file", result.documents[0].metadata)
        self.assertEqual(result.documents[0].metadata["block_number"], 1)

        # Check that open was called with the right path
        mock_file.assert_called_once_with("dummy_path.html", "r", encoding="utf-8")
        # Check that BeautifulSoup was called with the file handle and parser
        mock_bs.assert_called_once()
        # Check that get_text was called
        mock_soup.get_text.assert_called_once()


if __name__ == "__main__":
    unittest.main()
