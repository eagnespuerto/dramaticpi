import pytest

reportlab = pytest.importorskip("reportlab")

from dramaticpi.pdf import export_pdf
from tests.fixtures import screenplay_fixture, stage_fixture


def test_export_pdf_screenplay_writes_file_with_pdf_header(tmp_path):
    out = tmp_path / "kettle.pdf"
    export_pdf(screenplay_fixture(), str(out))
    data = out.read_bytes()
    assert data[:5] == b"%PDF-"
    assert b"612" in data
    assert b"792" in data


def test_export_pdf_stage_writes_file_with_pdf_header(tmp_path):
    out = tmp_path / "waiting.pdf"
    export_pdf(stage_fixture(), str(out))
    data = out.read_bytes()
    assert data[:5] == b"%PDF-"


def test_export_pdf_uses_courier(tmp_path):
    out = tmp_path / "font.pdf"
    export_pdf(screenplay_fixture(), str(out))
    data = out.read_bytes()
    assert b"Courier" in data


def test_export_pdf_title_page_when_metadata_present(tmp_path):
    from dramaticpi.model import Document
    out = tmp_path / "titled.pdf"
    export_pdf(
        Document(title="A Title", author="An Author",
                 blocks=screenplay_fixture().blocks),
        str(out),
    )
    data = out.read_bytes()
    assert b"A Title" in data
    assert b"An Author" in data
