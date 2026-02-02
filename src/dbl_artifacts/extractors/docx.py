"""DOCX text extraction using python-docx."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from ..detect import DOCX_EXTENSIONS, DOCX_MIME, ZIP_MAGIC
from ..errors import FailureRecord, ReasonCode
from ..models import ArtifactRecord
from ..storage import LocalStorage
from .base import ExtractedContent


class DocxExtractor:
    name = "docx"

    def supports(self, media_type: str, extension: str, magic_bytes: bytes) -> int:
        if media_type == DOCX_MIME:
            return 100
        if extension in DOCX_EXTENSIONS:
            return 90
        if magic_bytes.startswith(ZIP_MAGIC):
            return 50
        return 0

    def extract_text(self, artifact: ArtifactRecord, storage: LocalStorage, magic_bytes: bytes) -> list[ExtractedContent] | FailureRecord:
        try:
            from docx import Document  # type: ignore
        except Exception:
            return FailureRecord(ReasonCode.EXTRACT_DEPENDENCY_MISSING, "python-docx not installed", dependency="python-docx")

        try:
            data = storage.read_bytes(Path(artifact.storage_uri))
            doc = Document(BytesIO(data))
        except Exception as exc:
            return FailureRecord(ReasonCode.EXTRACT_PARSE_ERROR, str(exc))

        text = "\n".join(p.text for p in doc.paragraphs if p.text)
        output_name = f"{artifact.original_filename}.extracted.txt"
        return [ExtractedContent(content=text.encode("utf-8"), output_filename=output_name, media_type="text/plain")]
