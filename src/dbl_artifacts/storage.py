"""Local content-addressed storage backend."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .errors import ArtifactError, ReasonCode


@dataclass(frozen=True)
class LocalStorage:
    root: Path

    def ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for_hash(self, sha256_hex: str) -> Path:
        prefix_a = sha256_hex[:2]
        prefix_b = sha256_hex[2:4]
        return self.root / prefix_a / prefix_b / sha256_hex

    def store_bytes(self, content: bytes) -> Path:
        self.ensure()
        digest = sha256_bytes(content)
        path = self._path_for_hash(digest)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            try:
                path.write_bytes(content)
            except Exception as exc:
                raise ArtifactError(ReasonCode.STORAGE_WRITE_ERROR, str(exc)) from exc
        return path

    def read_bytes(self, path: Path) -> bytes:
        return path.read_bytes()

    def read_head(self, path: Path, limit: int = 512) -> bytes:
        with path.open("rb") as handle:
            return handle.read(limit)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
