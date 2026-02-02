"""Extractor drivers."""

from .docx import DocxExtractor
from .eml import EmlExtractor
from .html import HtmlExtractor
from .pdf import PdfExtractor
from .text import TextExtractor

__all__ = [
    "DocxExtractor",
    "EmlExtractor",
    "HtmlExtractor",
    "PdfExtractor",
    "TextExtractor",
]
