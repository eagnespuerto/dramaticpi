import pytest

from piscript.model import ElementType as E, Mode
from piscript.rules import (
    apply_heuristics, cycle_next, next_element,
    screenplay_tab_cycle, stage_tab_cycle,
)


@pytest.mark.parametrize("current,expected", [
    (E.SCENE_HEADING, E.ACTION),
    (E.ACTION, E.ACTION),
    (E.CHARACTER, E.DIALOGUE),
    (E.DIALOGUE, E.ACTION),
    (E.PARENTHETICAL, E.DIALOGUE),
    (E.TRANSITION, E.SCENE_HEADING),
])
def test_screenplay_enter_next(current, expected):
    assert next_element(Mode.SCREENPLAY, current) == expected


@pytest.mark.parametrize("current,expected", [
    (E.ACT_HEADING, E.SCENE_HEADING_STAGE),
    (E.SCENE_HEADING_STAGE, E.STAGE_DIRECTION),
    (E.STAGE_DIRECTION, E.CHARACTER),
    (E.CHARACTER, E.DIALOGUE),
    (E.DIALOGUE, E.CHARACTER),
    (E.SONG, E.CHARACTER),
])
def test_stage_enter_next(current, expected):
    assert next_element(Mode.STAGE, current) == expected


def test_screenplay_tab_cycle_order():
    assert screenplay_tab_cycle() == [
        E.SCENE_HEADING, E.ACTION, E.CHARACTER,
        E.PARENTHETICAL, E.DIALOGUE, E.TRANSITION,
    ]


def test_stage_tab_cycle_order():
    assert stage_tab_cycle() == [
        E.CHARACTER, E.DIALOGUE, E.STAGE_DIRECTION,
        E.SCENE_HEADING_STAGE, E.ACT_HEADING, E.SONG,
    ]


def test_cycle_next_wraps():
    last = screenplay_tab_cycle()[-1]
    assert cycle_next(Mode.SCREENPLAY, last) == screenplay_tab_cycle()[0]


def test_cycle_next_falls_back_when_current_not_in_cycle():
    assert cycle_next(Mode.SCREENPLAY, E.SONG) == screenplay_tab_cycle()[0]


def test_int_prefix_promotes_to_scene_heading():
    assert apply_heuristics(Mode.SCREENPLAY, E.ACTION, "INT. KITCHEN") == E.SCENE_HEADING


def test_ext_prefix_promotes_to_scene_heading():
    assert apply_heuristics(Mode.SCREENPLAY, E.ACTION, "ext. street - day") == E.SCENE_HEADING


def test_ie_prefix_promotes_to_scene_heading():
    assert apply_heuristics(Mode.SCREENPLAY, E.ACTION, "I/E. car - night") == E.SCENE_HEADING


def test_open_paren_after_character_promotes_to_parenthetical():
    assert apply_heuristics(Mode.SCREENPLAY, E.DIALOGUE, "(quietly)") == E.PARENTHETICAL


def test_heuristics_no_change_on_empty_text():
    assert apply_heuristics(Mode.SCREENPLAY, E.ACTION, "") == E.ACTION


def test_heuristics_no_change_when_not_applicable():
    assert apply_heuristics(Mode.SCREENPLAY, E.ACTION, "regular action line") == E.ACTION


def test_stage_mode_has_no_heuristics():
    assert apply_heuristics(Mode.STAGE, E.DIALOGUE, "INT. anything") == E.DIALOGUE
