"""EML extraction using Python stdlib email."""
from __future__ import annotations

from email import policy
from email.parser import BytesParser
from pathlib import Path

from ..detect import EML_EXTENSIONS, EML_MIME
from ..errors import FailureRecord, ReasonCode
from ..models import ArtifactRecord
from ..storage import LocalStorage
from .base import ExtractedContent


class EmlExtractor:
    name = "eml"

    def supports(self, media_type: str, extension: str, magic_bytes: bytes) -> int:
        if media_type == EML_MIME:
            return 100
        if extension in EML_EXTENSIONS:
            return 80
        return 0

    def extract_text(self, artifact: ArtifactRecord, storage: LocalStorage, magic_bytes: bytes) -> list[ExtractedContent] | FailureRecord:
        try:
            data = Path(artifact.storage_uri).read_bytes()
        except Exception as exc:
            return FailureRecord(ReasonCode.EXTRACT_PARSE_ERROR, str(exc))

        try:
            msg = BytesParser(policy=policy.default).parsebytes(data)
        except Exception as exc:
            return FailureRecord(ReasonCode.EXTRACT_PARSE_ERROR, str(exc))

        subject = msg.get("subject", "")
        sender = msg.get("from", "")
        to = msg.get("to", "")
        date = msg.get("date", "")

        body_text = _best_text_body(msg)
        if not body_text.strip():
            return FailureRecord(ReasonCode.EXTRACT_EMPTY_CONTENT, "empty email body")

        header = (
            f"Subject: {subject}\n"
            f"From: {sender}\n"
            f"To: {to}\n"
            f"Date: {date}\n\n"
        )
        outputs: list[ExtractedContent] = []
        output_name = f"{artifact.original_filename}.extracted.txt"
        outputs.append(
            ExtractedContent(content=(header + body_text).encode("utf-8"), output_filename=output_name, media_type="text/plain")
        )

        for attachment in _extract_attachments(msg, artifact.artifact_id):
            outputs.append(attachment)

        return outputs


def _best_text_body(msg) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    return part.get_content()
                except Exception:
                    continue
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                try:
                    from lxml import html as lxml_html  # type: ignore
                    tree = lxml_html.fromstring(part.get_content())
                    return tree.text_content()
                except Exception:
                    continue
        return ""
    try:
        return msg.get_content()
    except Exception:
        return ""


def _extract_attachments(msg, parent_id: str) -> list[ExtractedContent]:
    attachments: list[ExtractedContent] = []
    for part in msg.walk():
        if part.get_content_disposition() != "attachment":
            continue
        filename = part.get_filename() or "attachment"
        try:
            payload = part.get_payload(decode=True)
        except Exception:
            payload = None
        if not payload:
            continue
        media_type = part.get_content_type() or "application/octet-stream"
        output_name = f"{filename}"
        attachments.append(
            ExtractedContent(
                content=payload,
                output_filename=output_name,
                media_type=media_type,
                metadata={
                    "source": "attachment",
                    "attachment_name": filename,
                    "parent_artifact_id": parent_id,
                },
            )
        )
    return attachments
