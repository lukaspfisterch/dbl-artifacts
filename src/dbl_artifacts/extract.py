"""Extraction router."""
from __future__ import annotations

from pathlib import Path

from .detect import extension_from_filename
from .errors import FailureRecord, ReasonCode
from .models import ArtifactRecord, DerivationResult
from .registry import ExtractorRegistry, default_registry
from .storage import LocalStorage, sha256_bytes
from .extractors.base import ExtractedContent


def _default_storage() -> LocalStorage:
    return LocalStorage(Path.cwd() / "data")


def extract_text(
    artifact: ArtifactRecord,
    storage: LocalStorage | None = None,
    registry: ExtractorRegistry | None = None,
) -> DerivationResult:
    """Extract text from an artifact using the registered extractors."""
    store = storage or _default_storage()
    reg = registry or default_registry()

    extension = extension_from_filename(artifact.original_filename)
    try:
        magic = store.read_head(Path(artifact.storage_uri), 512)
    except Exception as exc:
        return DerivationResult.failed(FailureRecord(ReasonCode.EXTRACT_PARSE_ERROR, str(exc)))

    extractor = reg.select(artifact.media_type, extension, magic)
    if extractor is None:
        return DerivationResult.failed(
            FailureRecord(ReasonCode.EXTRACT_UNSUPPORTED_TYPE, f"unsupported file type: {extension}")
        )

    result = extractor.extract_text(artifact, store, magic)
    if isinstance(result, FailureRecord):
        return DerivationResult.failed(result)

    derived = [_store_derived(item, store) for item in result]
    return DerivationResult.success(derived)


def _store_derived(content: ExtractedContent, store: LocalStorage) -> ArtifactRecord:
    digest = sha256_bytes(content.content)
    path = store.store_bytes(content.content)
    return ArtifactRecord(
        artifact_id=f"art-{digest}",
        original_filename=content.output_filename,
        media_type=content.media_type,
        byte_size=len(content.content),
        sha256_bytes=digest,
        storage_uri=str(path),
        metadata=content.metadata,
    )
