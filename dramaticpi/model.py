"""Document, Block, and enums for DramaticPi."""

from __future__ import annotations

import json
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


class DocumentError(Exception):
    """Raised when a .dramapi file cannot be loaded."""


class UnsupportedVersionError(DocumentError):
    """Raised when the file was written by a newer DramaticPi."""


CURRENT_VERSION = 1


@dataclass
class LoadResult:
    document: Document
    warnings: list[str] = field(default_factory=list)


def from_dict(raw: dict) -> LoadResult:
    warnings: list[str] = []

    version = raw.get("version", CURRENT_VERSION)
    if not isinstance(version, int):
        raise DocumentError("version must be an integer")
    if version > CURRENT_VERSION:
        raise UnsupportedVersionError(
            f"file was written by a newer DramaticPi (version {version})"
        )

    mode_raw = raw.get("mode", Mode.SCREENPLAY.value)
    try:
        mode = Mode(mode_raw)
    except ValueError:
        warnings.append(f"unknown mode {mode_raw!r}, coerced to screenplay")
        mode = Mode.SCREENPLAY

    blocks: list[Block] = []
    for i, b in enumerate(raw.get("blocks", []) or []):
        t_raw = b.get("type", ElementType.ACTION.value)
        try:
            t = ElementType(t_raw)
        except ValueError:
            warnings.append(f"block {i}: unknown type {t_raw!r}, coerced to ACTION")
            t = ElementType.ACTION
        blocks.append(Block(type=t, text=str(b.get("text", ""))))

    doc = Document(
        version=version,
        mode=mode,
        title=str(raw.get("title", "Untitled")),
        author=str(raw.get("author", "")),
        contact=str(raw.get("contact", "")),
        draft_date=str(raw.get("draft_date", "")),
        blocks=blocks,
    )
    return LoadResult(document=doc, warnings=warnings)


def load(path: str) -> LoadResult:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return from_dict(raw)


def save(doc: Document, path: str) -> None:
    payload = {
        "version": doc.version,
        "mode": doc.mode.value,
        "title": doc.title,
        "author": doc.author,
        "contact": doc.contact,
        "draft_date": doc.draft_date,
        "blocks": [{"type": b.type.value, "text": b.text} for b in doc.blocks],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
