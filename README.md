# dbl-artifacts

Deterministic, domain-agnostic artifact import and extraction package.

It's simply a package which reduces my headache about handling various file formats and their metadata. It provides a consistent API for importing artifacts, extracting text, and storing results in a content-addressed manner.

## Public API

- `import_artifact(source, filename, media_type=None, storage=None) -> ArtifactRecord`
- `extract_text(artifact, storage=None, registry=None) -> DerivationResult`

## Supported formats

- Text: `.txt`, `.md`
- PDF: `application/pdf`
- DOCX: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- HTML: `.html`, `.htm`
- Email: `.eml` (RFC 5322)

Unsupported formats fail with explicit reason codes.

## Extraction outputs

- For PDF/DOCX/HTML/TXT/MD/EML: `<original>.extracted.txt` with `text/plain`
- For EML attachments: one artifact per attachment (metadata includes parent + filename)

## Determinism

- Content is stored using a content-addressed layout (sha256-based).
- Artifact IDs are derived from content hashes.
- No timestamps are included in digests.


## Potential gaps / next steps

- Tighten type detection (e.g., avoid treating any ZIP as DOCX without additional checks).
- Add a storage abstraction to support non-local backends and stable URI handling.
- Define normalization rules for extracted text (line endings, whitespace, metadata).
- Expand encoding detection beyond UTF-8/Latin-1 fallbacks.
- Add provenance/lineage metadata and a manifest export format.
- Provide a CLI or batch ingestion workflow.
