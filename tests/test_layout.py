from dramaticpi.layout import (
    Alignment, Case, FONT_NAME, FONT_SIZE_PT, POINTS_PER_INCH,
    SCREENPLAY_PAGE, STAGE_PAGE, page_metrics, style_for,
)
from dramaticpi.model import ElementType, Mode


def test_font_is_courier_12pt():
    assert FONT_NAME == "Courier"
    assert FONT_SIZE_PT == 12
    assert POINTS_PER_INCH == 72.0


def test_screenplay_page_metrics_are_us_letter_wga_margins():
    p = SCREENPLAY_PAGE
    assert p.width_inch == 8.5
    assert p.height_inch == 11.0
    assert p.left_inch == 1.5
    assert p.right_inch == 1.0
    assert p.top_inch == 1.0
    assert p.bottom_inch == 1.0


def test_stage_page_metrics_are_one_inch_all_sides():
    p = STAGE_PAGE
    assert p.width_inch == 8.5
    assert p.height_inch == 11.0
    assert p.left_inch == 1.0
    assert p.right_inch == 1.0
    assert p.top_inch == 1.0
    assert p.bottom_inch == 1.0


def test_page_metrics_dispatch_by_mode():
    assert page_metrics(Mode.SCREENPLAY) is SCREENPLAY_PAGE
    assert page_metrics(Mode.STAGE) is STAGE_PAGE


def _sc(elem):
    return style_for(Mode.SCREENPLAY, elem)


def test_screenplay_scene_heading():
    s = _sc(ElementType.SCENE_HEADING)
    assert s.left_inch == 1.5 and s.right_inch == 7.5
    assert s.alignment == Alignment.LEFT
    assert s.case == Case.UPPER


def test_screenplay_action():
    s = _sc(ElementType.ACTION)
    assert s.left_inch == 1.5 and s.right_inch == 7.5
    assert s.alignment == Alignment.LEFT
    assert s.case == Case.MIXED


def test_screenplay_character():
    s = _sc(ElementType.CHARACTER)
    assert s.left_inch == 3.7 and s.right_inch == 7.5
    assert s.alignment == Alignment.LEFT
    assert s.case == Case.UPPER


def test_screenplay_parenthetical():
    s = _sc(ElementType.PARENTHETICAL)
    assert s.left_inch == 3.1 and s.right_inch == 5.5
    assert s.case == Case.MIXED


def test_screenplay_dialogue():
    s = _sc(ElementType.DIALOGUE)
    assert s.left_inch == 2.5 and s.right_inch == 6.0
    assert s.case == Case.MIXED


def test_screenplay_transition():
    s = _sc(ElementType.TRANSITION)
    assert s.left_inch == 1.5 and s.right_inch == 7.5
    assert s.alignment == Alignment.RIGHT
    assert s.case == Case.UPPER


def _st(elem):
    return style_for(Mode.STAGE, elem)


def test_stage_act_heading_centered_upper_underlined():
    s = _st(ElementType.ACT_HEADING)
    assert s.alignment == Alignment.CENTER
    assert s.case == Case.UPPER
    assert s.underline is True


def test_stage_scene_heading_centered_upper():
    s = _st(ElementType.SCENE_HEADING_STAGE)
    assert s.alignment == Alignment.CENTER
    assert s.case == Case.UPPER


def test_stage_character_centered_upper():
    s = _st(ElementType.CHARACTER)
    assert s.alignment == Alignment.CENTER
    assert s.case == Case.UPPER


def test_stage_dialogue_full_width():
    s = _st(ElementType.DIALOGUE)
    assert s.left_inch == 1.0 and s.right_inch == 7.5
    assert s.alignment == Alignment.LEFT
    assert s.case == Case.MIXED


def test_stage_direction_indented_three_inches_italic():
    s = _st(ElementType.STAGE_DIRECTION)
    assert s.left_inch == 3.0
    assert s.italic is True


def test_stage_song_indented_one_point_five_italic():
    s = _st(ElementType.SONG)
    assert s.left_inch == 1.5
    assert s.italic is True
