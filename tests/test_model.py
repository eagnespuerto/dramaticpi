import json

import pytest

from piscript.model import (
    Block, Document, DocumentError, ElementType, LoadResult, Mode,
    UnsupportedVersionError, from_dict, load, save,
)


def doc_to_dict(doc: Document) -> dict:
    return {
        "version": doc.version,
        "mode": doc.mode.value,
        "title": doc.title,
        "author": doc.author,
        "contact": doc.contact,
        "draft_date": doc.draft_date,
        "blocks": [{"type": b.type.value, "text": b.text} for b in doc.blocks],
    }


def test_mode_values():
    assert Mode.SCREENPLAY.value == "screenplay"
    assert Mode.STAGE.value == "stage"


def test_element_type_values():
    for name in [
        "SCENE_HEADING", "ACTION", "CHARACTER", "DIALOGUE",
        "PARENTHETICAL", "TRANSITION",
        "ACT_HEADING", "SCENE_HEADING_STAGE", "STAGE_DIRECTION", "SONG",
    ]:
        assert ElementType[name].value == name


def test_block_defaults():
    b = Block(type=ElementType.ACTION)
    assert b.type == ElementType.ACTION
    assert b.text == ""


def test_document_defaults():
    d = Document()
    assert d.version == 1
    assert d.mode == Mode.SCREENPLAY
    assert d.title == "Untitled"
    assert d.author == ""
    assert d.contact == ""
    assert d.draft_date == ""
    assert d.blocks == []


def test_from_dict_minimal():
    result = from_dict({"version": 1, "mode": "screenplay", "blocks": []})
    assert result.document.mode == Mode.SCREENPLAY
    assert result.document.blocks == []
    assert result.warnings == []


def test_from_dict_coerces_unknown_mode():
    result = from_dict({"version": 1, "mode": "bogus", "blocks": []})
    assert result.document.mode == Mode.SCREENPLAY
    assert any("bogus" in w for w in result.warnings)


def test_from_dict_coerces_unknown_block_type():
    result = from_dict({
        "version": 1, "mode": "stage",
        "blocks": [{"type": "GIBBERISH", "text": "x"}],
    })
    assert result.document.blocks[0].type == ElementType.ACTION
    assert result.document.blocks[0].text == "x"
    assert any("GIBBERISH" in w for w in result.warnings)


def test_from_dict_rejects_future_version():
    with pytest.raises(UnsupportedVersionError):
        from_dict({"version": 2, "mode": "screenplay", "blocks": []})


def test_from_dict_rejects_non_integer_version():
    with pytest.raises(DocumentError):
        from_dict({"version": "one", "mode": "screenplay", "blocks": []})


def test_save_and_load_round_trip(tmp_path):
    doc = Document(
        mode=Mode.STAGE, title="Godot", author="Beckett",
        blocks=[
            Block(ElementType.ACT_HEADING, "ACT ONE"),
            Block(ElementType.CHARACTER, "VLADIMIR"),
            Block(ElementType.DIALOGUE, "Nothing to be done."),
        ],
    )
    path = tmp_path / "godot.piscript"
    save(doc, str(path))
    loaded = load(str(path)).document
    assert loaded == doc


def test_save_produces_valid_utf8_json_with_trailing_newline(tmp_path):
    doc = Document(title="Ünïcode ✓")
    path = tmp_path / "u.piscript"
    save(doc, str(path))
    raw = path.read_bytes()
    assert raw.endswith(b"\n")
    json.loads(raw.decode("utf-8"))
