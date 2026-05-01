import unittest
from unittest.mock import patch, mock_open, MagicMock

from moss_doc_parser.parsers.markdown import MarkdownParser
from moss_doc_parser.types import ParseResult


class TestMarkdownParser(unittest.TestCase):
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="# Title\n\nThis is a paragraph.",
    )
    @patch("moss_doc_parser.parsers.markdown.markdown.Markdown")
    @patch("moss_doc_parser.parsers.markdown.BeautifulSoup")
    def test_parse_returns_documents(self, mock_bs, mock_md, mock_file):
        # Setup mock for markdown conversion
        mock_md_instance = MagicMock()
        mock_md_instance.convert.return_value = (
            "<h1>Title</h1><p>This is a paragraph.</p>"
        )
        mock_md.return_value = mock_md_instance

        # Setup mock for BeautifulSoup
        mock_soup = MagicMock()
        # We need to mock the find_all method to return a list of elements
        # For simplicity, we'll return two elements: a header and a paragraph
        mock_h1 = MagicMock()
        mock_h1.name = "h1"
        mock_h1.get_text.return_value = "Title"
        mock_p = MagicMock()
        mock_p.name = "p"
        mock_p.get_text.return_value = "This is a paragraph."
        mock_soup.find_all.return_value = [mock_h1, mock_p]
        mock_bs.return_value = mock_soup

        parser = MarkdownParser()
        result = parser.parse("dummy_path.md")

        # Assertions
        self.assertIsInstance(result, ParseResult)
        # We expect at least two documents: one for the header and one for the paragraph
        self.assertGreaterEqual(len(result.documents), 2)
        # Check that the first document is the header
        self.assertEqual(result.documents[0].text, "Title")
        self.assertEqual(result.documents[0].metadata["type"], "header")
        # Check that the second document is the paragraph
        self.assertEqual(result.documents[1].text, "This is a paragraph.")
        self.assertEqual(result.documents[1].metadata["type"], "paragraph")

        # Check that open was called with the right path
        mock_file.assert_called_once_with("dummy_path.md", "r", encoding="utf-8")
        # Check that markdown was called
        mock_md.assert_called_once()
        # Check that BeautifulSoup was called with the markdown output
        mock_bs.assert_called_once()
        # Check that find_all was called on the soup object
        mock_soup.find_all.assert_called_once()


if __name__ == "__main__":
    unittest.main()
