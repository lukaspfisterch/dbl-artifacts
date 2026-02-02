"""PDF text extraction using PyMuPDF."""
from __future__ import annotations

from pathlib import Path

from ..detect import PDF_EXTENSIONS, PDF_MAGIC, PDF_MIME
from ..errors import FailureRecord, ReasonCode
from ..models import ArtifactRecord
from ..storage import LocalStorage
from .base import ExtractedContent


class PdfExtractor:
    name = "pdf"

    def supports(self, media_type: str, extension: str, magic_bytes: bytes) -> int:
        if media_type == PDF_MIME:
            return 100
        if extension in PDF_EXTENSIONS:
            return 90
        if magic_bytes.startswith(PDF_MAGIC):
            return 95
        return 0

    def extract_text(self, artifact: ArtifactRecord, storage: LocalStorage, magic_bytes: bytes) -> list[ExtractedContent] | FailureRecord:
        try:
            import fitz  # type: ignore
        except Exception as exc:
            return FailureRecord(ReasonCode.EXTRACT_DEPENDENCY_MISSING, "pymupdf not installed", dependency="pymupdf")

        try:
            data = storage.read_bytes(Path(artifact.storage_uri))
            doc = fitz.open(stream=data, filetype="pdf")
        except Exception as exc:
            return FailureRecord(ReasonCode.EXTRACT_PARSE_ERROR, str(exc))

        if doc.is_encrypted:
            return FailureRecord(ReasonCode.EXTRACT_PASSWORD_REQUIRED, "PDF is encrypted")

        try:
            text = "\n".join(page.get_text() for page in doc)
        except Exception as exc:
            return FailureRecord(ReasonCode.EXTRACT_PARSE_ERROR, str(exc))
        finally:
            doc.close()

        output_name = f"{artifact.original_filename}.extracted.txt"
        return [ExtractedContent(content=text.encode("utf-8"), output_filename=output_name, media_type="text/plain")]
