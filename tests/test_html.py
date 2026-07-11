import re

from dramaticpi.html import export_html
from dramaticpi.model import Block, Document, ElementType as E, Mode
from tests.fixtures import screenplay_fixture, stage_fixture


def test_export_html_has_courier_style_and_letter_size():
    html = export_html(screenplay_fixture())
    assert "<!DOCTYPE html>" in html
    assert "Courier" in html
    assert re.search(r"@page\s*\{[^}]*size:\s*letter", html, re.IGNORECASE) is not None


def test_export_html_screenplay_margins_are_wga():
    html = export_html(screenplay_fixture())
    assert re.search(r"margin:\s*1in\s+1in\s+1in\s+1\.5in", html) is not None


def test_export_html_stage_margins_are_one_inch_all_sides():
    html = export_html(stage_fixture())
    assert re.search(r"margin:\s*1in\s+1in\s+1in\s+1in", html) is not None


def test_export_html_page_breaks_have_visible_markers():
    doc = Document(mode=Mode.SCREENPLAY, blocks=[
        Block(E.ACTION, "line " + str(i)) for i in range(200)
    ])
    html = export_html(doc)
    assert html.count('class="page-break"') >= 1
    assert 'class="page-number"' in html


def test_export_html_stage_uses_stage_class_names():
    html = export_html(stage_fixture())
    assert "block ACT_HEADING" in html
    assert "block CHARACTER" in html
    assert "block DIALOGUE" in html


def test_export_html_escapes_user_input():
    doc = Document(blocks=[Block(E.ACTION, "<script>alert('x')</script>")])
    html = export_html(doc)
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html
