"""Deterministic type detection utilities."""
from __future__ import annotations

from pathlib import Path

PDF_MAGIC = b"%PDF"
ZIP_MAGIC = b"PK\x03\x04"

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
PDF_MIME = "application/pdf"
TEXT_MIME = "text/plain"
HTML_MIME = "text/html"
EML_MIME = "message/rfc822"

TEXT_EXTENSIONS = {".txt", ".md"}
PDF_EXTENSIONS = {".pdf"}
DOCX_EXTENSIONS = {".docx"}
HTML_EXTENSIONS = {".html", ".htm"}
EML_EXTENSIONS = {".eml"}


def extension_from_filename(filename: str) -> str:
    return Path(filename).suffix.lower()


def detect_media_type(filename: str, provided: str | None, head: bytes) -> str:
    if provided:
        return provided
    ext = extension_from_filename(filename)
    if ext in TEXT_EXTENSIONS:
        return TEXT_MIME
    if ext in PDF_EXTENSIONS or head.startswith(PDF_MAGIC):
        return PDF_MIME
    if ext in DOCX_EXTENSIONS or head.startswith(ZIP_MAGIC):
        return DOCX_MIME
    if ext in HTML_EXTENSIONS:
        return HTML_MIME
    if ext in EML_EXTENSIONS:
        return EML_MIME
    return "application/octet-stream"


def is_supported_import(media_type: str, extension: str, head: bytes) -> bool:
    if extension in TEXT_EXTENSIONS:
        return True
    if extension in PDF_EXTENSIONS or media_type == PDF_MIME or head.startswith(PDF_MAGIC):
        return True
    if extension in DOCX_EXTENSIONS or media_type == DOCX_MIME or head.startswith(ZIP_MAGIC):
        return True
    if extension in HTML_EXTENSIONS or media_type == HTML_MIME:
        return True
    if extension in EML_EXTENSIONS or media_type == EML_MIME:
        return True
    return False
