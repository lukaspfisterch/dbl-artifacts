"""Plain text extractor."""
from __future__ import annotations

from pathlib import Path

from ..detect import TEXT_EXTENSIONS
from ..errors import FailureRecord, ReasonCode
from ..models import ArtifactRecord
from ..storage import LocalStorage
from .base import ExtractedContent


class TextExtractor:
    name = "text"

    def supports(self, media_type: str, extension: str, magic_bytes: bytes) -> int:
        if extension in TEXT_EXTENSIONS:
            return 90
        if media_type.startswith("text/"):
            return 80
        return 0

    def extract_text(self, artifact: ArtifactRecord, storage: LocalStorage, magic_bytes: bytes) -> list[ExtractedContent] | FailureRecord:
        try:
            text = Path(artifact.storage_uri).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                text = Path(artifact.storage_uri).read_text(encoding="latin-1")
            except Exception as exc:
                return FailureRecord(ReasonCode.EXTRACT_PARSE_ERROR, str(exc))
        except Exception as exc:
            return FailureRecord(ReasonCode.EXTRACT_PARSE_ERROR, str(exc))

        output_name = f"{artifact.original_filename}.extracted.txt"
        return [ExtractedContent(content=text.encode("utf-8"), output_filename=output_name, media_type="text/plain")]
