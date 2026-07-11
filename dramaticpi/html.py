"""Self-contained HTML export with visible page markings.

Produces a single .html file with an inline <style> — no JavaScript, no
external assets. `@page` rules give correct print margins; on-screen we
paginate approximately by line-count (§3 page metrics) and emit an
`<hr class="page-break">` + page label between simulated pages.
"""

from __future__ import annotations

from html import escape

from .layout import (
    Alignment, Case, FONT_NAME, FONT_SIZE_PT,
    ElementStyle, all_styles, page_metrics, style_for,
)
from .model import Block, Document, Mode


def _fmt_in(n: float) -> str:
    """Format inches without a trailing '.0' for whole numbers."""
    return f"{int(n)}in" if float(n).is_integer() else f"{n}in"


def export_html(doc: Document) -> str:
    metrics = page_metrics(doc.mode)
    title = escape(doc.title or "DramaticPi document")

    css = _build_css(doc.mode, metrics)
    body = _build_body(doc)

    return (
        f"<!DOCTYPE html>\n"
        f"<html lang=\"en\">\n"
        f"<head>\n"
        f"<meta charset=\"utf-8\">\n"
        f"<title>{title}</title>\n"
        f"<style>\n{css}\n</style>\n"
        f"</head>\n"
        f"<body>\n{body}\n</body>\n"
        f"</html>\n"
    )


def _build_css(mode: Mode, metrics) -> str:
    at_page = (
        f"@page {{ size: letter; "
        f"margin: {_fmt_in(metrics.top_inch)} {_fmt_in(metrics.right_inch)} "
        f"{_fmt_in(metrics.bottom_inch)} {_fmt_in(metrics.left_inch)}; }}"
    )

    page_box = (
        f".page {{ "
        f"width: {_fmt_in(metrics.width_inch)}; "
        f"min-height: {_fmt_in(metrics.height_inch)}; "
        f"padding: {_fmt_in(metrics.top_inch)} {_fmt_in(metrics.right_inch)} "
        f"{_fmt_in(metrics.bottom_inch)} {_fmt_in(metrics.left_inch)}; "
        f"margin: 1em auto; background: white; box-sizing: border-box; "
        f"box-shadow: 0 0 4px rgba(0,0,0,0.1); "
        f"}}"
    )

    base = (
        f"body {{ font-family: '{FONT_NAME}', 'Courier New', monospace; "
        f"font-size: {FONT_SIZE_PT}pt; line-height: {FONT_SIZE_PT}pt; "
        f"background: #eee; color: black; margin: 0; }}"
    )

    per_element: list[str] = []
    for elem, style in all_styles(mode).items():
        per_element.append(_css_for(elem.value, style, metrics))

    breaks = (
        ".page-break { border: none; border-top: 1px dashed #999; margin: 1em 0; }\n"
        ".page-number { text-align: center; font-size: 9pt; color: #666; margin: 0.25em 0 1em 0; }\n"
        "@media print { .page-break, .page-number { display: none; } "
        ".page { box-shadow: none; margin: 0; page-break-after: always; padding: 0; } }"
    )

    return "\n".join([base, at_page, page_box, *per_element, breaks])


def _css_for(class_name: str, style: ElementStyle, metrics) -> str:
    left = max(style.left_inch - metrics.left_inch, 0.0)
    right_page_edge = metrics.width_inch - metrics.right_inch
    right = max(right_page_edge - style.right_inch, 0.0)

    align = {Alignment.LEFT: "left", Alignment.CENTER: "center",
             Alignment.RIGHT: "right"}[style.alignment]
    parts = [
        f"margin: {style.space_before_lines * FONT_SIZE_PT}pt 0 "
        f"{style.space_after_lines * FONT_SIZE_PT}pt 0",
        f"padding-left: {_fmt_in(left)}",
        f"padding-right: {_fmt_in(right)}",
        f"text-align: {align}",
        f"text-transform: {'uppercase' if style.case == Case.UPPER else 'none'}",
    ]
    if style.italic:
        parts.append("font-style: italic")
    if style.underline:
        parts.append("text-decoration: underline")
    return f".block.{class_name} {{ {'; '.join(parts)}; }}"


def _build_body(doc: Document) -> str:
    metrics = page_metrics(doc.mode)
    body_lines_per_page = metrics.lines_per_page

    pages: list[list[str]] = [[]]
    used_lines = 0

    for block in doc.blocks:
        style = style_for(doc.mode, block.type)
        cost = 1 + style.space_before_lines + style.space_after_lines
        if used_lines + cost > body_lines_per_page and pages[-1]:
            pages.append([])
            used_lines = 0
        pages[-1].append(_render_block(block))
        used_lines += cost

    out: list[str] = []
    for i, page in enumerate(pages):
        out.append('<div class="page">')
        out.extend(page)
        out.append('</div>')
        if i < len(pages) - 1:
            out.append('<hr class="page-break">')
            out.append(f'<div class="page-number">Page {i + 1} of {len(pages)}</div>')
    return "\n".join(out)


def _render_block(block: Block) -> str:
    text = escape(block.text).replace("\n", "<br>")
    return f'<p class="block {block.type.value}">{text or "&nbsp;"}</p>'
