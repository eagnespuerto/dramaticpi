"""PDF export via ReportLab.

Uses the same layout tables as the on-screen editor (see layout.py) so what
you see is what prints.
"""

from __future__ import annotations

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Frame, PageBreak, PageTemplate,
    Paragraph, SimpleDocTemplate, Spacer,
)

from .layout import (
    Alignment, Case, FONT_NAME, FONT_SIZE_PT, POINTS_PER_INCH,
    ElementStyle, page_metrics, style_for,
)
from .model import Document, Mode


LINE_HEIGHT_PT = FONT_SIZE_PT


def export_pdf(doc: Document, path: str) -> None:
    metrics = page_metrics(doc.mode)
    page_w = metrics.width_inch * POINTS_PER_INCH
    page_h = metrics.height_inch * POINTS_PER_INCH
    top_margin = metrics.top_inch * POINTS_PER_INCH
    bottom_margin = metrics.bottom_inch * POINTS_PER_INCH

    frame = Frame(
        0, bottom_margin,
        page_w, page_h - top_margin - bottom_margin,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id="body",
    )
    body_template = PageTemplate(id="body", frames=[frame], pagesize=letter)

    sdt = SimpleDocTemplate(
        path, pagesize=letter,
        leftMargin=0, rightMargin=0,
        topMargin=top_margin, bottomMargin=bottom_margin,
        title=doc.title, author=doc.author,
    )
    sdt.addPageTemplates([body_template])

    story: list = []

    if doc.title or doc.author or doc.contact or doc.draft_date:
        story.extend(_title_page_flowables(doc, page_w, page_h))
        story.append(PageBreak())

    for block in doc.blocks:
        story.append(_flowable_for(block, doc.mode))

    sdt.build(story)


def _title_page_flowables(doc: Document, page_w: float, page_h: float) -> list:
    center = ParagraphStyle(
        "TitleCenter", fontName=FONT_NAME, fontSize=FONT_SIZE_PT,
        alignment=1, leading=LINE_HEIGHT_PT,
    )
    flow: list = [Spacer(1, page_h * 0.3)]
    if doc.title:
        flow.append(Paragraph(doc.title.upper(), center))
        flow.append(Spacer(1, 24))
    if doc.author:
        flow.append(Paragraph(f"by {doc.author}", center))
        flow.append(Spacer(1, 48))
    if doc.contact:
        flow.append(Paragraph(doc.contact.replace("\n", "<br/>"), center))
    if doc.draft_date:
        flow.append(Spacer(1, 24))
        flow.append(Paragraph(doc.draft_date, center))
    return flow


def _alignment_to_rl(a: Alignment) -> int:
    return {Alignment.LEFT: 0, Alignment.CENTER: 1, Alignment.RIGHT: 2}[a]


def _apply_case(text: str, case: Case) -> str:
    return text.upper() if case == Case.UPPER else text


def _flowable_for(block, mode: Mode) -> Paragraph:
    metrics = page_metrics(mode)
    style: ElementStyle = style_for(mode, block.type)

    left_pt = style.left_inch * POINTS_PER_INCH
    right_from_left = (metrics.width_inch - style.right_inch) * POINTS_PER_INCH

    para_style = ParagraphStyle(
        f"E-{block.type.value}",
        fontName=FONT_NAME,
        fontSize=FONT_SIZE_PT,
        leading=LINE_HEIGHT_PT,
        alignment=_alignment_to_rl(style.alignment),
        leftIndent=left_pt,
        rightIndent=right_from_left,
        spaceBefore=style.space_before_lines * LINE_HEIGHT_PT,
        spaceAfter=style.space_after_lines * LINE_HEIGHT_PT,
        underline=style.underline,
    )
    text = _apply_case(block.text, style.case)
    if style.italic:
        text = f"<i>{text}</i>"
    if style.underline:
        text = f"<u>{text}</u>"
    return Paragraph(text or "&nbsp;", para_style)
