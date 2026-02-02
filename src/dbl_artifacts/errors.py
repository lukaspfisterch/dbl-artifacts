"""Error taxonomy for dbl-artifacts."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReasonCode(str, Enum):
    IMPORT_UNSUPPORTED_TYPE = "IMPORT_UNSUPPORTED_TYPE"
    IMPORT_READ_ERROR = "IMPORT_READ_ERROR"
    STORAGE_WRITE_ERROR = "STORAGE_WRITE_ERROR"
    EXTRACT_UNSUPPORTED_TYPE = "EXTRACT_UNSUPPORTED_TYPE"
    EXTRACT_ENCRYPTED_DOCUMENT = "EXTRACT_ENCRYPTED_DOCUMENT"
    EXTRACT_PASSWORD_REQUIRED = "EXTRACT_PASSWORD_REQUIRED"
    EXTRACT_PARSE_ERROR = "EXTRACT_PARSE_ERROR"
    EXTRACT_EMPTY_CONTENT = "EXTRACT_EMPTY_CONTENT"
    EXTRACT_OCR_REQUIRED = "EXTRACT_OCR_REQUIRED"
    EXTRACT_TRANSCRIBE_FAILED = "EXTRACT_TRANSCRIBE_FAILED"
    EXTRACT_DEPENDENCY_MISSING = "EXTRACT_DEPENDENCY_MISSING"


@dataclass(frozen=True)
class FailureRecord:
    reason_code: ReasonCode
    detail: str
    dependency: str | None = None
    status_code: int | None = None


@dataclass(frozen=True)
class ArtifactError(Exception):
    """Deterministic failure for API-level errors."""

    reason_code: ReasonCode
    detail: str

    def __str__(self) -> str:
        return f"{self.reason_code}: {self.detail}"
