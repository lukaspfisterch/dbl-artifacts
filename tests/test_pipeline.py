from email.message import EmailMessage
from pathlib import Path

import pytest

from dbl_artifacts import LocalStorage, import_artifact, extract_text


def test_txt_import_and_extract(tmp_path: Path) -> None:
    storage = LocalStorage(tmp_path / "store")
    input_path = tmp_path / "note.txt"
    input_path.write_text("hello world", encoding="utf-8")

    artifact = import_artifact(input_path, "note.txt", storage=storage)
    result = extract_text(artifact, storage=storage)

    assert result.failure is None
    assert result.derived_artifacts is not None
    assert result.derived_artifacts[0].original_filename.endswith(".extracted.txt")


def test_pdf_import_and_extract(tmp_path: Path) -> None:
    try:
        import fitz  # type: ignore
    except Exception:
        pytest.skip("pymupdf not installed")

    storage = LocalStorage(tmp_path / "store")
    pdf_path = tmp_path / "sample.pdf"

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello PDF")
    doc.save(pdf_path)
    doc.close()

    artifact = import_artifact(pdf_path, "sample.pdf", storage=storage)
    result = extract_text(artifact, storage=storage)

    assert result.failure is None
    assert result.derived_artifacts is not None
    text = Path(result.derived_artifacts[0].storage_uri).read_text(encoding="utf-8")
    assert "Hello" in text


def test_docx_import_and_extract(tmp_path: Path) -> None:
    try:
        from docx import Document  # type: ignore
    except Exception:
        pytest.skip("python-docx not installed")

    storage = LocalStorage(tmp_path / "store")
    docx_path = tmp_path / "sample.docx"

    document = Document()
    document.add_paragraph("Hello DOCX")
    document.save(docx_path)

    artifact = import_artifact(docx_path, "sample.docx", storage=storage)
    result = extract_text(artifact, storage=storage)

    assert result.failure is None
    assert result.derived_artifacts is not None
    text = Path(result.derived_artifacts[0].storage_uri).read_text(encoding="utf-8")
    assert "Hello" in text


def test_html_import_and_extract(tmp_path: Path) -> None:
    try:
        import readability  # type: ignore
        import lxml  # type: ignore
    except Exception:
        pytest.skip("readability-lxml or lxml not installed")

    storage = LocalStorage(tmp_path / "store")
    html_path = tmp_path / "page.html"
    html_path.write_text("<html><head><title>T</title></head><body><p>Hello HTML</p></body></html>", encoding="utf-8")

    artifact = import_artifact(html_path, "page.html", storage=storage)
    result = extract_text(artifact, storage=storage)

    assert result.failure is None
    assert result.derived_artifacts is not None
    text = Path(result.derived_artifacts[0].storage_uri).read_text(encoding="utf-8")
    assert "Hello HTML" in text


def test_eml_import_and_extract_with_attachment(tmp_path: Path) -> None:
    try:
        import lxml  # type: ignore
    except Exception:
        pytest.skip("lxml not installed")

    storage = LocalStorage(tmp_path / "store")
    eml_path = tmp_path / "message.eml"

    msg = EmailMessage()
    msg["Subject"] = "Test"
    msg["From"] = "alice@example.com"
    msg["To"] = "bob@example.com"
    msg.set_content("Plain body")
    msg.add_alternative("<html><body><p>HTML body</p></body></html>", subtype="html")
    msg.add_attachment(b"att content", maintype="text", subtype="plain", filename="note.txt")

    eml_path.write_bytes(msg.as_bytes())

    artifact = import_artifact(eml_path, "message.eml", storage=storage)
    result = extract_text(artifact, storage=storage)

    assert result.failure is None
    assert result.derived_artifacts is not None
    names = [a.original_filename for a in result.derived_artifacts]
    assert any(name.endswith(".extracted.txt") for name in names)
    assert "note.txt" in names
    attachment = next(a for a in result.derived_artifacts if a.original_filename == "note.txt")
    assert attachment.metadata is not None
    assert attachment.metadata.get("parent_artifact_id") == artifact.artifact_id
