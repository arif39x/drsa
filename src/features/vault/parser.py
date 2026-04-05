import os
from pathlib import Path

class TechDocParser:
    # Technical document parser specializing in LaTeX and complex layouts.

    def __init__(self):
        pass

    def parse_technical_pdf(self, pdf_path):
        try:
            from marker.convert import convert_single_pdf
            # Parse PDF using marker-pdf to preserve LaTeX formulas and tables.
            text, _, _ = convert_single_pdf(str(pdf_path), None, None)
            return text
        except ImportError:
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(pdf_path)
                return "\\n".join(page.get_text() for page in doc)
            except ImportError:
                return "Failed: marker-pdf and PyMuPDF are not installed."

    def parse_office_doc(self, doc_path):
        try:
            from markitdown import MarkItDown
            mid = MarkItDown()
            result = mid.convert(doc_path)
            return result.text_content
        except ImportError:
            return "MarkItDown not installed. Falling back to simple text."
