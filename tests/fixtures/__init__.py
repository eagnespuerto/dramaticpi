"""Test fixtures for DramaticPi."""

from dramaticpi.model import Block, Document, ElementType as E, Mode


def screenplay_fixture() -> Document:
    return Document(
        mode=Mode.SCREENPLAY,
        title="Kettle",
        author="A. Writer",
        blocks=[
            Block(E.SCENE_HEADING, "INT. KITCHEN - NIGHT"),
            Block(E.ACTION, "MAYA stares at the kettle. Steam rises."),
            Block(E.CHARACTER, "MAYA"),
            Block(E.PARENTHETICAL, "(quiet)"),
            Block(E.DIALOGUE, "Boil already."),
            Block(E.ACTION, "The kettle whistles. She smiles."),
            Block(E.TRANSITION, "CUT TO:"),
            Block(E.SCENE_HEADING, "EXT. STREET - DAY"),
            Block(E.ACTION, "She walks."),
        ],
    )


def stage_fixture() -> Document:
    return Document(
        mode=Mode.STAGE,
        title="Waiting",
        author="S. B.",
        blocks=[
            Block(E.ACT_HEADING, "ACT ONE"),
            Block(E.SCENE_HEADING_STAGE, "SCENE 1"),
            Block(E.STAGE_DIRECTION, "A tree. Evening."),
            Block(E.CHARACTER, "VLADIMIR"),
            Block(E.DIALOGUE, "Nothing to be done."),
            Block(E.CHARACTER, "ESTRAGON"),
            Block(E.DIALOGUE, "I'm beginning to come round to that opinion."),
            Block(E.SONG, "La la la, la la la."),
        ],
    )
