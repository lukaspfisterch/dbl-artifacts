"""Core models for dbl-artifacts."""
from __future__ import annotations

from dataclasses import dataclass

from .errors import FailureRecord

JOB_IMPORT = "artifact.import"
JOB_EXTRACT_TEXT = "artifact.extract_text"


@dataclass(frozen=True)
class ArtifactRecord:
    artifact_id: str
    original_filename: str
    media_type: str
    byte_size: int
    sha256_bytes: str
    storage_uri: str
    metadata: dict[str, str] | None = None


@dataclass(frozen=True)
class DerivationResult:
    derived_artifacts: list[ArtifactRecord] | None
    failure: FailureRecord | None

    @classmethod
    def success(cls, artifacts: list[ArtifactRecord]) -> "DerivationResult":
        return cls(derived_artifacts=artifacts, failure=None)

    @classmethod
    def failed(cls, failure: FailureRecord) -> "DerivationResult":
        return cls(derived_artifacts=None, failure=failure)
