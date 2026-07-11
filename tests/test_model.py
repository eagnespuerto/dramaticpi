from piscript.model import Block, Document, ElementType, Mode


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
