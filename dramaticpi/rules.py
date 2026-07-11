"""Element transition rules and content heuristics.

Encoded from the design spec §6. All functions are pure.
"""

from __future__ import annotations

import re

from .model import ElementType, Mode


_SCREENPLAY_ENTER_NEXT: dict[ElementType, ElementType] = {
    ElementType.SCENE_HEADING: ElementType.ACTION,
    ElementType.ACTION:        ElementType.ACTION,
    ElementType.CHARACTER:     ElementType.DIALOGUE,
    ElementType.DIALOGUE:      ElementType.ACTION,
    ElementType.PARENTHETICAL: ElementType.DIALOGUE,
    ElementType.TRANSITION:    ElementType.SCENE_HEADING,
}

_STAGE_ENTER_NEXT: dict[ElementType, ElementType] = {
    ElementType.ACT_HEADING:         ElementType.SCENE_HEADING_STAGE,
    ElementType.SCENE_HEADING_STAGE: ElementType.STAGE_DIRECTION,
    ElementType.STAGE_DIRECTION:     ElementType.CHARACTER,
    ElementType.CHARACTER:           ElementType.DIALOGUE,
    ElementType.DIALOGUE:            ElementType.CHARACTER,
    ElementType.SONG:                ElementType.CHARACTER,
}

_SCREENPLAY_TAB_CYCLE = [
    ElementType.SCENE_HEADING, ElementType.ACTION, ElementType.CHARACTER,
    ElementType.PARENTHETICAL, ElementType.DIALOGUE, ElementType.TRANSITION,
]

_STAGE_TAB_CYCLE = [
    ElementType.CHARACTER, ElementType.DIALOGUE, ElementType.STAGE_DIRECTION,
    ElementType.SCENE_HEADING_STAGE, ElementType.ACT_HEADING, ElementType.SONG,
]

_SCENE_HEADING_RE = re.compile(r"^\s*(int\.|ext\.|i/e\.)", re.IGNORECASE)


def screenplay_tab_cycle() -> list[ElementType]:
    return list(_SCREENPLAY_TAB_CYCLE)


def stage_tab_cycle() -> list[ElementType]:
    return list(_STAGE_TAB_CYCLE)


def next_element(mode: Mode, current: ElementType) -> ElementType:
    table = _SCREENPLAY_ENTER_NEXT if mode == Mode.SCREENPLAY else _STAGE_ENTER_NEXT
    default = ElementType.ACTION if mode == Mode.SCREENPLAY else ElementType.DIALOGUE
    return table.get(current, default)


def cycle_next(mode: Mode, current: ElementType) -> ElementType:
    cycle = _SCREENPLAY_TAB_CYCLE if mode == Mode.SCREENPLAY else _STAGE_TAB_CYCLE
    if current not in cycle:
        return cycle[0]
    return cycle[(cycle.index(current) + 1) % len(cycle)]


def apply_heuristics(mode: Mode, current: ElementType, text: str) -> ElementType:
    """Look at what the user just typed and possibly re-classify the block."""
    if not text or mode != Mode.SCREENPLAY:
        return current
    if _SCENE_HEADING_RE.match(text) and current == ElementType.ACTION:
        return ElementType.SCENE_HEADING
    if text.startswith("(") and current in (ElementType.CHARACTER, ElementType.DIALOGUE):
        return ElementType.PARENTHETICAL
    return current
