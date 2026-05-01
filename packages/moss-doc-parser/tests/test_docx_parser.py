import unittest
from unittest.mock import patch, MagicMock

from moss_doc_parser.parsers.docx import DocxParser
from moss_doc_parser.types import ParseResult


class TestDocxParser(unittest.TestCase):
    @patch("moss_doc_parser.parsers.docx.DocxDocument")
    def test_parse_returns_documents(self, mock_docx):
        mock_paragraph = MagicMock()
        mock_paragraph.text = "This is a paragraph."
        mock_docx.return_value.paragraphs = [mock_paragraph]

        parser = DocxParser()
        result = parser.parse("dummy_path.docx")

        self.assertIsInstance(result, ParseResult)
        self.assertEqual(len(result.documents), 1)
        self.assertEqual(result.documents[0].text, "This is a paragraph.")
        self.assertIn("source_file", result.documents[0].metadata)
        self.assertEqual(result.documents[0].metadata["paragraph_number"], 1)
        self.assertEqual(result.documents[0].metadata["total_paragraphs"], 1)

        mock_docx.assert_called_once_with("dummy_path.docx")


if __name__ == "__main__":
    unittest.main()