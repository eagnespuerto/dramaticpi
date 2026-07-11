"""Layout tables: WGA screenplay + Dramatists Guild stage.

Single source of truth for the editor, PDF export, and HTML export.
Numbers here are the industry-standard values from the design spec §3.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .model import ElementType, Mode


POINTS_PER_INCH = 72.0
FONT_NAME = "Courier"
FONT_SIZE_PT = 12


class Alignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class Case(str, Enum):
    UPPER = "upper"
    MIXED = "mixed"


@dataclass(frozen=True)
class ElementStyle:
    left_inch: float
    right_inch: float
    alignment: Alignment
    case: Case
    italic: bool = False
    underline: bool = False
    space_before_lines: int = 0
    space_after_lines: int = 0


@dataclass(frozen=True)
class PageMetrics:
    width_inch: float
    height_inch: float
    top_inch: float
    bottom_inch: float
    left_inch: float
    right_inch: float
    lines_per_page: int


SCREENPLAY_PAGE = PageMetrics(
    width_inch=8.5, height_inch=11.0,
    top_inch=1.0, bottom_inch=1.0,
    left_inch=1.5, right_inch=1.0,
    lines_per_page=55,
)

STAGE_PAGE = PageMetrics(
    width_inch=8.5, height_inch=11.0,
    top_inch=1.0, bottom_inch=1.0,
    left_inch=1.0, right_inch=1.0,
    lines_per_page=55,
)

_SCREENPLAY: dict[ElementType, ElementStyle] = {
    ElementType.SCENE_HEADING: ElementStyle(1.5, 7.5, Alignment.LEFT, Case.UPPER, space_before_lines=1),
    ElementType.ACTION:        ElementStyle(1.5, 7.5, Alignment.LEFT, Case.MIXED),
    ElementType.CHARACTER:     ElementStyle(3.7, 7.5, Alignment.LEFT, Case.UPPER, space_before_lines=1),
    ElementType.PARENTHETICAL: ElementStyle(3.1, 5.5, Alignment.LEFT, Case.MIXED),
    ElementType.DIALOGUE:      ElementStyle(2.5, 6.0, Alignment.LEFT, Case.MIXED),
    ElementType.TRANSITION:    ElementStyle(1.5, 7.5, Alignment.RIGHT, Case.UPPER, space_before_lines=1),
}

_STAGE: dict[ElementType, ElementStyle] = {
    ElementType.ACT_HEADING:         ElementStyle(1.0, 7.5, Alignment.CENTER, Case.UPPER, underline=True, space_before_lines=2, space_after_lines=2),
    ElementType.SCENE_HEADING_STAGE: ElementStyle(1.0, 7.5, Alignment.CENTER, Case.UPPER, space_after_lines=1),
    ElementType.CHARACTER:           ElementStyle(1.0, 7.5, Alignment.CENTER, Case.UPPER, space_before_lines=1),
    ElementType.DIALOGUE:            ElementStyle(1.0, 7.5, Alignment.LEFT, Case.MIXED),
    ElementType.STAGE_DIRECTION:     ElementStyle(3.0, 7.5, Alignment.LEFT, Case.MIXED, italic=True, space_before_lines=1, space_after_lines=1),
    ElementType.SONG:                ElementStyle(1.5, 7.5, Alignment.LEFT, Case.MIXED, italic=True),
}

_DEFAULT_SCREENPLAY = _SCREENPLAY[ElementType.ACTION]
_DEFAULT_STAGE = _STAGE[ElementType.DIALOGUE]


def page_metrics(mode: Mode) -> PageMetrics:
    return SCREENPLAY_PAGE if mode == Mode.SCREENPLAY else STAGE_PAGE


def style_for(mode: Mode, element: ElementType) -> ElementStyle:
    table = _SCREENPLAY if mode == Mode.SCREENPLAY else _STAGE
    if element in table:
        return table[element]
    return _DEFAULT_SCREENPLAY if mode == Mode.SCREENPLAY else _DEFAULT_STAGE


def valid_elements(mode: Mode) -> list[ElementType]:
    """Element types applicable to this mode, in the toolbar dropdown order."""
    if mode == Mode.SCREENPLAY:
        return [
            ElementType.SCENE_HEADING, ElementType.ACTION,
            ElementType.CHARACTER, ElementType.PARENTHETICAL,
            ElementType.DIALOGUE, ElementType.TRANSITION,
        ]
    return [
        ElementType.ACT_HEADING, ElementType.SCENE_HEADING_STAGE,
        ElementType.CHARACTER, ElementType.DIALOGUE,
        ElementType.STAGE_DIRECTION, ElementType.SONG,
    ]


def all_styles(mode: Mode) -> dict[ElementType, ElementStyle]:
    return dict(_SCREENPLAY) if mode == Mode.SCREENPLAY else dict(_STAGE)
