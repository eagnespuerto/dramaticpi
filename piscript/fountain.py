"""Fountain (screenplay markup) import/export — best-effort, lossy on stage."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .model import Block, Document, ElementType, Mode


_STAGE_ONLY = {
    ElementType.ACT_HEADING,
    ElementType.SCENE_HEADING_STAGE,
    ElementType.STAGE_DIRECTION,
    ElementType.SONG,
}

_INT_EXT_RE = re.compile(r"^\s*(int\.|ext\.|i/e\.)", re.IGNORECASE)
_NOTE_RE = re.compile(r"^\s*\[\[([A-Z_]+):\s*(.*)\]\]\s*$")


@dataclass
class ExportResult:
    text: str
    warnings: list[str] = field(default_factory=list)


@dataclass
class ImportResult:
    document: Document
    warnings: list[str] = field(default_factory=list)


def export_fountain(doc: Document) -> ExportResult:
    lines: list[str] = []
    warnings: list[str] = []

    title_page: list[str] = []
    if doc.title:
        title_page.append(f"Title: {doc.title}")
    if doc.author:
        title_page.append(f"Author: {doc.author}")
    if doc.contact:
        title_page.append(f"Contact: {doc.contact}")
    if doc.draft_date:
        title_page.append(f"Draft date: {doc.draft_date}")
    if title_page:
        lines.extend(title_page)
        lines.append("")

    had_stage_only = False
    for block in doc.blocks:
        t, text = block.type, block.text
        if t in _STAGE_ONLY:
            had_stage_only = True
            lines.append(f"[[{t.value}: {text}]]")
        elif t == ElementType.SCENE_HEADING:
            if _INT_EXT_RE.match(text):
                lines.append(text)
            else:
                lines.append(f".{text}")
        elif t == ElementType.ACTION:
            lines.append(text)
        elif t == ElementType.CHARACTER:
            lines.append(text)
        elif t == ElementType.PARENTHETICAL:
            lines.append(text if text.startswith("(") else f"({text})")
        elif t == ElementType.DIALOGUE:
            lines.append(text)
        elif t == ElementType.TRANSITION:
            lines.append(f"> {text}")
        else:
            lines.append(text)
        lines.append("")

    if had_stage_only:
        warnings.append(
            "Stage-only elements were exported as Fountain notes ([[…]]) — "
            "this is a lossy conversion and may not survive round-tripping "
            "through other tools."
        )

    return ExportResult(text="\n".join(lines).rstrip() + "\n", warnings=warnings)


def parse_fountain(src: str) -> ImportResult:
    """Parse a Fountain document into a screenplay-mode Document.

    Best-effort. Preserves stage-only elements when marked with our
    `[[TYPE: text]]` note convention. Unknown lines become ACTION.
    """
    warnings: list[str] = []
    doc = Document(mode=Mode.SCREENPLAY)

    paragraphs = re.split(r"\n\s*\n", src.strip())
    prev_type: ElementType | None = None

    for para in paragraphs:
        para = para.rstrip()
        if not para:
            continue

        if prev_type is None and _try_title_page(para, doc):
            continue

        lines = para.split("\n")
        first = lines[0]

        m = _NOTE_RE.match(first)
        if m and len(lines) == 1:
            type_name, body = m.group(1), m.group(2)
            try:
                t = ElementType(type_name)
            except ValueError:
                warnings.append(f"unknown note type {type_name!r}, treated as ACTION")
                t = ElementType.ACTION
            doc.blocks.append(Block(type=t, text=body))
            prev_type = t
            continue

        if first.startswith("."):
            doc.blocks.append(Block(ElementType.SCENE_HEADING, first[1:].strip()))
            prev_type = ElementType.SCENE_HEADING
            continue

        if _INT_EXT_RE.match(first) and len(lines) == 1:
            doc.blocks.append(Block(ElementType.SCENE_HEADING, first))
            prev_type = ElementType.SCENE_HEADING
            continue

        if first.startswith(">") and len(lines) == 1:
            doc.blocks.append(Block(ElementType.TRANSITION, first[1:].strip()))
            prev_type = ElementType.TRANSITION
            continue

        if first.strip().isupper() and first.strip() and len(lines) > 1:
            doc.blocks.append(Block(ElementType.CHARACTER, first.strip()))
            for rest in lines[1:]:
                if rest.startswith("(") and rest.endswith(")"):
                    doc.blocks.append(Block(ElementType.PARENTHETICAL, rest))
                else:
                    doc.blocks.append(Block(ElementType.DIALOGUE, rest))
            prev_type = ElementType.DIALOGUE
            continue

        if first.strip().isupper() and first.strip():
            doc.blocks.append(Block(ElementType.CHARACTER, first.strip()))
            prev_type = ElementType.CHARACTER
            continue

        doc.blocks.append(Block(ElementType.ACTION, para))
        prev_type = ElementType.ACTION

    return ImportResult(document=doc, warnings=warnings)


_TITLE_PAGE_KEYS = {
    "title": "title", "author": "author",
    "contact": "contact", "draft date": "draft_date",
}


def _try_title_page(para: str, doc: Document) -> bool:
    lines = para.split("\n")
    kv: dict[str, str] = {}
    for line in lines:
        if ":" not in line:
            return False
        k, v = line.split(":", 1)
        key = k.strip().lower()
        if key not in _TITLE_PAGE_KEYS:
            return False
        kv[_TITLE_PAGE_KEYS[key]] = v.strip()
    for attr, value in kv.items():
        setattr(doc, attr, value)
    return True
