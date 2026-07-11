from dramaticpi.fountain import (
    ExportResult, ImportResult, export_fountain, parse_fountain,
)
from dramaticpi.model import Block, Document, ElementType as E, Mode


def test_export_screenplay_basic():
    doc = Document(
        mode=Mode.SCREENPLAY,
        title="Untitled",
        blocks=[
            Block(E.SCENE_HEADING, "INT. KITCHEN - NIGHT"),
            Block(E.ACTION, "MAYA stares at the kettle."),
            Block(E.CHARACTER, "MAYA"),
            Block(E.PARENTHETICAL, "(quiet)"),
            Block(E.DIALOGUE, "Boil already."),
            Block(E.TRANSITION, "CUT TO:"),
        ],
    )
    result = export_fountain(doc)
    assert isinstance(result, ExportResult)
    assert "INT. KITCHEN - NIGHT" in result.text
    assert "MAYA stares at the kettle." in result.text
    assert "MAYA\n" in result.text
    assert "(quiet)" in result.text
    assert "Boil already." in result.text
    assert "> CUT TO:" in result.text
    assert result.warnings == []


def test_export_screenplay_forces_scene_heading_when_needed():
    doc = Document(
        mode=Mode.SCREENPLAY,
        blocks=[Block(E.SCENE_HEADING, "SOMEWHERE ELSE")],
    )
    result = export_fountain(doc)
    assert ".SOMEWHERE ELSE" in result.text


def test_export_stage_warns_and_exports_stage_only_as_notes():
    doc = Document(
        mode=Mode.STAGE,
        blocks=[
            Block(E.ACT_HEADING, "ACT ONE"),
            Block(E.SCENE_HEADING_STAGE, "SCENE 1"),
            Block(E.STAGE_DIRECTION, "The lights come up."),
            Block(E.CHARACTER, "VLADIMIR"),
            Block(E.DIALOGUE, "Nothing to be done."),
            Block(E.SONG, "La la la"),
        ],
    )
    result = export_fountain(doc)
    assert "[[ACT_HEADING: ACT ONE]]" in result.text
    assert "[[SCENE_HEADING_STAGE: SCENE 1]]" in result.text
    assert "[[STAGE_DIRECTION: The lights come up.]]" in result.text
    assert "[[SONG: La la la]]" in result.text
    assert any("lossy" in w.lower() for w in result.warnings)


def test_export_includes_title_page_when_metadata_present():
    doc = Document(
        title="Godot", author="Beckett", contact="agent@example.com",
        draft_date="2026-07-11",
    )
    result = export_fountain(doc)
    assert "Title: Godot" in result.text
    assert "Author: Beckett" in result.text
    assert "Contact: agent@example.com" in result.text
    assert "Draft date: 2026-07-11" in result.text


def test_import_screenplay_basic():
    src = (
        "INT. KITCHEN - NIGHT\n"
        "\n"
        "MAYA stares at the kettle.\n"
        "\n"
        "MAYA\n"
        "(quiet)\n"
        "Boil already.\n"
        "\n"
        "> CUT TO:\n"
    )
    result = parse_fountain(src)
    assert isinstance(result, ImportResult)
    types = [b.type for b in result.document.blocks]
    assert types == [
        E.SCENE_HEADING, E.ACTION, E.CHARACTER,
        E.PARENTHETICAL, E.DIALOGUE, E.TRANSITION,
    ]
    assert result.document.blocks[0].text == "INT. KITCHEN - NIGHT"
    assert result.document.blocks[-1].text == "CUT TO:"


def test_import_forced_scene_heading():
    src = ".SOMEWHERE ELSE\n\nAction line.\n"
    result = parse_fountain(src)
    assert result.document.blocks[0].type == E.SCENE_HEADING
    assert result.document.blocks[0].text == "SOMEWHERE ELSE"


def test_import_note_with_stage_marker_restores_type():
    src = "[[ACT_HEADING: ACT ONE]]\n\n[[SONG: La la la]]\n"
    result = parse_fountain(src)
    types = [b.type for b in result.document.blocks]
    assert types == [E.ACT_HEADING, E.SONG]


def test_import_unknown_line_becomes_action_with_no_error():
    src = "Just some prose without markers.\n"
    result = parse_fountain(src)
    assert result.document.blocks[0].type == E.ACTION
