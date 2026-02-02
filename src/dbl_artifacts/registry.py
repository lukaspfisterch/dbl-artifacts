"""Extractor registry and selection."""
from __future__ import annotations

from dataclasses import dataclass

from .extractors.docx import DocxExtractor
from .extractors.eml import EmlExtractor
from .extractors.html import HtmlExtractor
from .extractors.pdf import PdfExtractor
from .extractors.text import TextExtractor
from .extractors.base import Extractor


@dataclass
class ExtractorRegistry:
    extractors: list[Extractor]

    def select(self, media_type: str, extension: str, magic_bytes: bytes) -> Extractor | None:
        scored: list[tuple[int, str, Extractor]] = []
        for extractor in self.extractors:
            score = extractor.supports(media_type, extension, magic_bytes)
            if score > 0:
                scored.append((score, extractor.name, extractor))
        if not scored:
            return None
        scored.sort(key=lambda item: (-item[0], item[1]))
        return scored[0][2]


def default_registry() -> ExtractorRegistry:
    return ExtractorRegistry(
        extractors=[
            TextExtractor(),
            PdfExtractor(),
            DocxExtractor(),
            HtmlExtractor(),
            EmlExtractor(),
        ]
    )
