"""Artifact import logic."""
from __future__ import annotations

from pathlib import Path

from .detect import detect_media_type, extension_from_filename, is_supported_import
from .errors import ArtifactError, FailureRecord, ReasonCode
from .models import ArtifactRecord
from .storage import LocalStorage, sha256_bytes


def _default_storage() -> LocalStorage:
    return LocalStorage(Path.cwd() / "data")


def _read_source(source: bytes | str | Path) -> bytes:
    if isinstance(source, bytes):
        return source
    path = Path(source)
    return path.read_bytes()


def import_artifact(
    source: bytes | str | Path,
    filename: str,
    media_type: str | None = None,
    storage: LocalStorage | None = None,
) -> ArtifactRecord:
    """Import a file into content-addressed storage.

    Raises ArtifactError on unsupported types or read failures.
    """
    store = storage or _default_storage()
    try:
        data = _read_source(source)
    except Exception as exc:
        raise ArtifactError(ReasonCode.IMPORT_READ_ERROR, str(exc)) from exc

    head = data[:512]
    ext = extension_from_filename(filename)
    detected_media = detect_media_type(filename, media_type, head)

    if not is_supported_import(detected_media, ext, head):
        raise ArtifactError(
            ReasonCode.IMPORT_UNSUPPORTED_TYPE,
            f"unsupported file type: {ext}",
        )

    digest = sha256_bytes(data)
    path = store.store_bytes(data)

    return ArtifactRecord(
        artifact_id=f"art-{digest}",
        original_filename=filename,
        media_type=detected_media,
        byte_size=len(data),
        sha256_bytes=digest,
        storage_uri=str(path),
    )
