"""HTML extraction using readability-lxml."""
from __future__ import annotations

from pathlib import Path

from ..detect import HTML_EXTENSIONS, HTML_MIME
from ..errors import FailureRecord, ReasonCode
from ..models import ArtifactRecord
from ..storage import LocalStorage
from .base import ExtractedContent


class HtmlExtractor:
    name = "html"

    def supports(self, media_type: str, extension: str, magic_bytes: bytes) -> int:
        if media_type == HTML_MIME:
            return 100
        if extension in HTML_EXTENSIONS:
            return 80
        return 0

    def extract_text(self, artifact: ArtifactRecord, storage: LocalStorage, magic_bytes: bytes) -> list[ExtractedContent] | FailureRecord:
        try:
            from readability import Document  # type: ignore
        except Exception:
            return FailureRecord(ReasonCode.EXTRACT_DEPENDENCY_MISSING, "readability-lxml not installed", dependency="readability-lxml")
        try:
            from lxml import html as lxml_html  # type: ignore
        except Exception:
            return FailureRecord(ReasonCode.EXTRACT_DEPENDENCY_MISSING, "lxml not installed", dependency="lxml")

        try:
            raw = Path(artifact.storage_uri).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                raw = Path(artifact.storage_uri).read_text(encoding="latin-1")
            except Exception as exc:
                return FailureRecord(ReasonCode.EXTRACT_PARSE_ERROR, str(exc))
        except Exception as exc:
            return FailureRecord(ReasonCode.EXTRACT_PARSE_ERROR, str(exc))

        try:
            doc = Document(raw)
            title = doc.short_title()
            content = doc.summary()
            tree = lxml_html.fromstring(content)
            text = tree.text_content()
        except Exception as exc:
            return FailureRecord(ReasonCode.EXTRACT_PARSE_ERROR, str(exc))

        header = f"Title: {title}\nSource: {artifact.original_filename}\n\n"
        output_name = f"{artifact.original_filename}.extracted.txt"
        return [ExtractedContent(content=(header + text).encode("utf-8"), output_filename=output_name, media_type="text/plain")]
