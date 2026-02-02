"""Extractor interfaces."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..errors import FailureRecord
from ..models import ArtifactRecord
from ..storage import LocalStorage


@dataclass(frozen=True)
class ExtractedContent:
    content: bytes
    output_filename: str
    media_type: str
    metadata: dict[str, str] | None = None


class Extractor(Protocol):
    name: str

    def supports(self, media_type: str, extension: str, magic_bytes: bytes) -> int:
        """Return a score > 0 if supported."""

    def extract_text(self, artifact: ArtifactRecord, storage: LocalStorage, magic_bytes: bytes) -> list[ExtractedContent] | FailureRecord:
        """Return extracted content items or a failure record."""
