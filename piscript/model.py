"""Document, Block, and enums for piscript."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Mode(str, Enum):
    SCREENPLAY = "screenplay"
    STAGE = "stage"


class ElementType(str, Enum):
    CHARACTER = "CHARACTER"
    DIALOGUE = "DIALOGUE"
    SCENE_HEADING = "SCENE_HEADING"
    ACTION = "ACTION"
    PARENTHETICAL = "PARENTHETICAL"
    TRANSITION = "TRANSITION"
    ACT_HEADING = "ACT_HEADING"
    SCENE_HEADING_STAGE = "SCENE_HEADING_STAGE"
    STAGE_DIRECTION = "STAGE_DIRECTION"
    SONG = "SONG"


@dataclass
class Block:
    type: ElementType
    text: str = ""


@dataclass
class Document:
    version: int = 1
    mode: Mode = Mode.SCREENPLAY
    title: str = "Untitled"
    author: str = ""
    contact: str = ""
    draft_date: str = ""
    blocks: list[Block] = field(default_factory=list)
