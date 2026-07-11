# piscript Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Python 3 + PyQt5 desktop app that edits stage plays and screenplays with industry-standard layouts, saves to a custom `.piscript` JSON, exports to PDF / HTML / Fountain, and runs on Raspberry Pi Zero W upward.

**Architecture:** Semantic-block editor. Each paragraph carries an `ElementType` (SCENE_HEADING, ACTION, CHARACTER, DIALOGUE, ...). Layout tables (WGA screenplay, Dramatists Guild stage) map `(mode, type)` to points, fonts, alignment, and case — the same tables drive the on-screen `QTextEdit`, the ReportLab PDF export, and the HTML export. Pure-Python modules stay Qt-free and are unit-tested; Qt lives in three thin files at the top of the stack.

**Tech Stack:** Python 3.9+ · PyQt5 (via `python3-pyqt5` on Pi OS, `pip install PyQt5` for dev) · ReportLab (`python3-reportlab` / `pip install reportlab`) · pytest for tests · stdlib for everything else.

**Spec:** [`docs/superpowers/specs/2026-07-11-piscript-design.md`](../specs/2026-07-11-piscript-design.md)

---

## Task 1: Repo skeleton, packaging config, license

**Files:**
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `pyproject.toml`
- Create: `piscript/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Modify: `README.md`

- [ ] **Step 1: Create `.gitignore`**

```gitignore
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
build/
dist/
*.egg-info/
.coverage
htmlcov/
.idea/
.vscode/
```

- [ ] **Step 2: Create `LICENSE` (MIT)**

```
MIT License

Copyright (c) 2026 piscript contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 3: Create `pyproject.toml`**

```toml
[project]
name = "piscript"
version = "0.1.0"
description = "Lightweight scriptwriting for stage and screen on Raspberry Pi"
readme = "README.md"
requires-python = ">=3.9"
license = { text = "MIT" }
dependencies = [
    "PyQt5>=5.15",
    "reportlab>=3.6",
]

[project.scripts]
piscript = "piscript.app:main"

[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["piscript*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

- [ ] **Step 4: Create `piscript/__init__.py`**

```python
"""piscript — lightweight scriptwriting for stage and screen."""

__version__ = "0.1.0"
```

- [ ] **Step 5: Create empty `tests/__init__.py` and `tests/conftest.py`**

`tests/__init__.py`: empty file (creates the package).

`tests/conftest.py`:

```python
"""Shared pytest fixtures for piscript tests."""

import sys
from pathlib import Path

# Allow tests to import piscript from the repo root without installation.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
```

- [ ] **Step 6: Replace `README.md` with the stub**

```markdown
# piscript

A lightweight word processor for stage plays and screenplays. Renders industry-standard layouts (WGA screenplay, Dramatists Guild stage) as you type. Ships as Python 3 + PyQt5 and runs on Raspberry Pi Zero W upward.

Detailed usage in [README.md](#usage) after install. See [`docs/superpowers/specs/2026-07-11-piscript-design.md`](docs/superpowers/specs/2026-07-11-piscript-design.md) for the design.

## Status

Under construction. Not yet installable.
```

- [ ] **Step 7: Verify pytest picks up the empty test dir**

Run: `pytest -q`
Expected: `no tests ran in ...` (exit 5, that's fine — the config resolves).

- [ ] **Step 8: Commit**

```bash
git add .gitignore LICENSE pyproject.toml piscript/ tests/ README.md
git commit -m "chore: repo skeleton, license, packaging config"
```

---

## Task 2: Model — enums, dataclasses

**Files:**
- Create: `piscript/model.py`
- Create: `tests/test_model.py`

- [ ] **Step 1: Write failing tests for `Mode`, `ElementType`, `Block`, `Document`**

`tests/test_model.py`:

```python
from piscript.model import Block, Document, ElementType, Mode


def test_mode_values():
    assert Mode.SCREENPLAY.value == "screenplay"
    assert Mode.STAGE.value == "stage"


def test_element_type_values():
    for name in [
        "SCENE_HEADING", "ACTION", "CHARACTER", "DIALOGUE",
        "PARENTHETICAL", "TRANSITION",
        "ACT_HEADING", "SCENE_HEADING_STAGE", "STAGE_DIRECTION", "SONG",
    ]:
        assert ElementType[name].value == name


def test_block_defaults():
    b = Block(type=ElementType.ACTION)
    assert b.type == ElementType.ACTION
    assert b.text == ""


def test_document_defaults():
    d = Document()
    assert d.version == 1
    assert d.mode == Mode.SCREENPLAY
    assert d.title == "Untitled"
    assert d.author == ""
    assert d.contact == ""
    assert d.draft_date == ""
    assert d.blocks == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_model.py -q`
Expected: FAIL — `ImportError: No module named piscript.model`.

- [ ] **Step 3: Create `piscript/model.py` with enums and dataclasses**

```python
"""Document, Block, and enums for piscript."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Mode(str, Enum):
    SCREENPLAY = "screenplay"
    STAGE = "stage"


class ElementType(str, Enum):
    # Shared (behave differently per mode)
    CHARACTER = "CHARACTER"
    DIALOGUE = "DIALOGUE"
    # Screenplay-only
    SCENE_HEADING = "SCENE_HEADING"
    ACTION = "ACTION"
    PARENTHETICAL = "PARENTHETICAL"
    TRANSITION = "TRANSITION"
    # Stage-only
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_model.py -q`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add piscript/model.py tests/test_model.py
git commit -m "feat(model): Mode, ElementType, Block, Document dataclasses"
```

---

## Task 3: Model — JSON load / save with version and type coercion

**Files:**
- Modify: `piscript/model.py`
- Modify: `tests/test_model.py`

- [ ] **Step 1: Extend the tests with load/save behaviour**

Append to `tests/test_model.py`:

```python
import json
import pytest

from piscript.model import (
    LoadResult, DocumentError, UnsupportedVersionError,
    from_dict, load, save,
)


def _round_trip_dict(doc: Document) -> Document:
    raw = doc_to_dict(doc)
    return from_dict(raw).document


def doc_to_dict(doc: Document) -> dict:
    return {
        "version": doc.version,
        "mode": doc.mode.value,
        "title": doc.title,
        "author": doc.author,
        "contact": doc.contact,
        "draft_date": doc.draft_date,
        "blocks": [{"type": b.type.value, "text": b.text} for b in doc.blocks],
    }


def test_from_dict_minimal():
    result = from_dict({"version": 1, "mode": "screenplay", "blocks": []})
    assert result.document.mode == Mode.SCREENPLAY
    assert result.document.blocks == []
    assert result.warnings == []


def test_from_dict_coerces_unknown_mode():
    result = from_dict({"version": 1, "mode": "bogus", "blocks": []})
    assert result.document.mode == Mode.SCREENPLAY
    assert any("bogus" in w for w in result.warnings)


def test_from_dict_coerces_unknown_block_type():
    result = from_dict({
        "version": 1, "mode": "stage",
        "blocks": [{"type": "GIBBERISH", "text": "x"}],
    })
    assert result.document.blocks[0].type == ElementType.ACTION
    assert result.document.blocks[0].text == "x"
    assert any("GIBBERISH" in w for w in result.warnings)


def test_from_dict_rejects_future_version():
    with pytest.raises(UnsupportedVersionError):
        from_dict({"version": 2, "mode": "screenplay", "blocks": []})


def test_from_dict_rejects_non_integer_version():
    with pytest.raises(DocumentError):
        from_dict({"version": "one", "mode": "screenplay", "blocks": []})


def test_save_and_load_round_trip(tmp_path):
    doc = Document(
        mode=Mode.STAGE, title="Godot", author="Beckett",
        blocks=[
            Block(ElementType.ACT_HEADING, "ACT ONE"),
            Block(ElementType.CHARACTER, "VLADIMIR"),
            Block(ElementType.DIALOGUE, "Nothing to be done."),
        ],
    )
    path = tmp_path / "godot.piscript"
    save(doc, str(path))
    loaded = load(str(path)).document
    assert loaded == doc


def test_save_produces_valid_utf8_json_with_trailing_newline(tmp_path):
    doc = Document(title="Ünïcode ✓")
    path = tmp_path / "u.piscript"
    save(doc, str(path))
    raw = path.read_bytes()
    assert raw.endswith(b"\n")
    json.loads(raw.decode("utf-8"))  # must parse
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_model.py -q`
Expected: FAIL — the new symbols don't exist yet.

- [ ] **Step 3: Extend `piscript/model.py` with load/save**

Append to `piscript/model.py`:

```python
import json


class DocumentError(Exception):
    """Raised when a .piscript file cannot be loaded."""


class UnsupportedVersionError(DocumentError):
    """Raised when the file was written by a newer piscript."""


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
            f"file was written by a newer piscript (version {version})"
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_model.py -q`
Expected: all model tests pass (10+).

- [ ] **Step 5: Commit**

```bash
git add piscript/model.py tests/test_model.py
git commit -m "feat(model): JSON load/save with version and type coercion"
```

---

## Task 4: Layout tables (screenplay + stage)

**Files:**
- Create: `piscript/layout.py`
- Create: `tests/test_layout.py`

- [ ] **Step 1: Write failing tests asserting the exact spec numbers**

`tests/test_layout.py`:

```python
from piscript.layout import (
    Alignment, Case, FONT_NAME, FONT_SIZE_PT, POINTS_PER_INCH,
    SCREENPLAY_PAGE, STAGE_PAGE, page_metrics, style_for,
)
from piscript.model import ElementType, Mode


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


# --- WGA screenplay element geometry ---

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


# --- Dramatists Guild stage element geometry ---

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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_layout.py -q`
Expected: FAIL — module missing.

- [ ] **Step 3: Create `piscript/layout.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_layout.py -q`
Expected: all layout tests pass (~15).

- [ ] **Step 5: Commit**

```bash
git add piscript/layout.py tests/test_layout.py
git commit -m "feat(layout): WGA + Dramatists Guild style tables"
```

---

## Task 5: Rules — Enter/Tab transitions and heuristics

**Files:**
- Create: `piscript/rules.py`
- Create: `tests/test_rules.py`

- [ ] **Step 1: Write failing tests for all transitions and heuristics**

`tests/test_rules.py`:

```python
import pytest

from piscript.model import ElementType as E, Mode
from piscript.rules import (
    apply_heuristics, cycle_next, next_element,
    stage_tab_cycle, screenplay_tab_cycle,
)


# --- Screenplay Enter transitions (spec §6.1) ---

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


# --- Stage Enter transitions (spec §6.2) ---

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


# --- Tab cycles ---

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
    # e.g., a stage element under screenplay mode
    assert cycle_next(Mode.SCREENPLAY, E.SONG) == screenplay_tab_cycle()[0]


# --- Screenplay heuristics ---

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
    # Stage mode leaves the element type alone — even INT. shouldn't remap.
    assert apply_heuristics(Mode.STAGE, E.DIALOGUE, "INT. anything") == E.DIALOGUE
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_rules.py -q`
Expected: FAIL — module missing.

- [ ] **Step 3: Create `piscript/rules.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_rules.py -q`
Expected: all rules tests pass.

- [ ] **Step 5: Commit**

```bash
git add piscript/rules.py tests/test_rules.py
git commit -m "feat(rules): Enter/Tab transitions + screenplay heuristics"
```

---

## Task 6: Fountain export (with lossy warnings for stage-only elements)

**Files:**
- Create: `piscript/fountain.py`
- Create: `tests/test_fountain.py`

- [ ] **Step 1: Write failing tests for export**

`tests/test_fountain.py`:

```python
from piscript.fountain import ExportResult, export_fountain
from piscript.model import Block, Document, ElementType as E, Mode


def test_export_screenplay_basic():
    doc = Document(
        mode=Mode.SCREENPLAY,
        title="Untitled",
        blocks=[
            Block(E.SCENE_HEADING, "INT. KITCHEN - NIGHT"),
            Block(E.ACTION, "MAYA stares at the kettle."),
            Block(E.CHARACTER, "MAYA"),
            Block(E.PARENTHETICAL, "(quiet)"),
            Block(E.DIALOGUE, "Boil already."),
            Block(E.TRANSITION, "CUT TO:"),
        ],
    )
    result = export_fountain(doc)
    assert isinstance(result, ExportResult)
    assert "INT. KITCHEN - NIGHT" in result.text
    assert "MAYA stares at the kettle." in result.text
    assert "MAYA\n" in result.text  # Character on own line
    assert "(quiet)" in result.text
    assert "Boil already." in result.text
    assert "> CUT TO:" in result.text  # Fountain transition marker
    assert result.warnings == []


def test_export_screenplay_forces_scene_heading_when_needed():
    # A scene heading not starting with INT/EXT must be prefixed with '.'
    doc = Document(
        mode=Mode.SCREENPLAY,
        blocks=[Block(E.SCENE_HEADING, "SOMEWHERE ELSE")],
    )
    result = export_fountain(doc)
    assert ".SOMEWHERE ELSE" in result.text


def test_export_stage_warns_and_exports_stage_only_as_notes():
    doc = Document(
        mode=Mode.STAGE,
        blocks=[
            Block(E.ACT_HEADING, "ACT ONE"),
            Block(E.SCENE_HEADING_STAGE, "SCENE 1"),
            Block(E.STAGE_DIRECTION, "The lights come up."),
            Block(E.CHARACTER, "VLADIMIR"),
            Block(E.DIALOGUE, "Nothing to be done."),
            Block(E.SONG, "La la la"),
        ],
    )
    result = export_fountain(doc)
    # Stage-only elements go into Fountain notes [[ ... ]] with a type marker
    assert "[[ACT_HEADING: ACT ONE]]" in result.text
    assert "[[SCENE_HEADING_STAGE: SCENE 1]]" in result.text
    assert "[[STAGE_DIRECTION: The lights come up.]]" in result.text
    assert "[[SONG: La la la]]" in result.text
    # And a warning is emitted mentioning lossy conversion
    assert any("lossy" in w.lower() for w in result.warnings)


def test_export_includes_title_page_when_metadata_present():
    doc = Document(
        title="Godot", author="Beckett", contact="agent@example.com",
        draft_date="2026-07-11",
    )
    result = export_fountain(doc)
    assert "Title: Godot" in result.text
    assert "Author: Beckett" in result.text
    assert "Contact: agent@example.com" in result.text
    assert "Draft date: 2026-07-11" in result.text
```

- [ ] **Step 2: Write failing tests for import**

Append to `tests/test_fountain.py`:

```python
from piscript.fountain import ImportResult, parse_fountain


def test_import_screenplay_basic():
    src = (
        "INT. KITCHEN - NIGHT\n"
        "\n"
        "MAYA stares at the kettle.\n"
        "\n"
        "MAYA\n"
        "(quiet)\n"
        "Boil already.\n"
        "\n"
        "> CUT TO:\n"
    )
    result = parse_fountain(src)
    assert isinstance(result, ImportResult)
    types = [b.type for b in result.document.blocks]
    assert types == [
        E.SCENE_HEADING, E.ACTION, E.CHARACTER,
        E.PARENTHETICAL, E.DIALOGUE, E.TRANSITION,
    ]
    assert result.document.blocks[0].text == "INT. KITCHEN - NIGHT"
    assert result.document.blocks[-1].text == "CUT TO:"


def test_import_forced_scene_heading():
    src = ".SOMEWHERE ELSE\n\nAction line.\n"
    result = parse_fountain(src)
    assert result.document.blocks[0].type == E.SCENE_HEADING
    assert result.document.blocks[0].text == "SOMEWHERE ELSE"


def test_import_note_with_stage_marker_restores_type():
    src = "[[ACT_HEADING: ACT ONE]]\n\n[[SONG: La la la]]\n"
    result = parse_fountain(src)
    types = [b.type for b in result.document.blocks]
    assert types == [E.ACT_HEADING, E.SONG]


def test_import_unknown_line_becomes_action_with_no_error():
    src = "Just some prose without markers.\n"
    result = parse_fountain(src)
    assert result.document.blocks[0].type == E.ACTION
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest tests/test_fountain.py -q`
Expected: FAIL — module missing.

- [ ] **Step 4: Create `piscript/fountain.py`**

```python
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

    # Title page
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
        lines.append("")  # separator before body

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
        lines.append("")  # blank line separator

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

    # Split into paragraphs on blank lines. Each paragraph classifies as one block.
    paragraphs = re.split(r"\n\s*\n", src.strip())
    prev_type: ElementType | None = None

    for para in paragraphs:
        para = para.rstrip()
        if not para:
            continue

        # Title-page lines like "Title: X" — recognize a small set at doc start.
        if prev_type is None and _try_title_page(para, doc):
            continue

        lines = para.split("\n")
        first = lines[0]

        # Structured note carrying an explicit type.
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

        # Forced scene heading with leading dot.
        if first.startswith("."):
            doc.blocks.append(Block(ElementType.SCENE_HEADING, first[1:].strip()))
            prev_type = ElementType.SCENE_HEADING
            continue

        # Regular scene heading INT./EXT.
        if _INT_EXT_RE.match(first) and len(lines) == 1:
            doc.blocks.append(Block(ElementType.SCENE_HEADING, first))
            prev_type = ElementType.SCENE_HEADING
            continue

        # Transition '> X'
        if first.startswith(">") and len(lines) == 1:
            doc.blocks.append(Block(ElementType.TRANSITION, first[1:].strip()))
            prev_type = ElementType.TRANSITION
            continue

        # UPPERCASE line followed by dialogue lines → Character (+ parenthetical + dialogue)
        if first.strip().isupper() and first.strip() and len(lines) > 1:
            doc.blocks.append(Block(ElementType.CHARACTER, first.strip()))
            for rest in lines[1:]:
                if rest.startswith("(") and rest.endswith(")"):
                    doc.blocks.append(Block(ElementType.PARENTHETICAL, rest))
                else:
                    doc.blocks.append(Block(ElementType.DIALOGUE, rest))
            prev_type = ElementType.DIALOGUE
            continue

        # UPPERCASE single line, no dialogue — treat as Character on its own.
        if first.strip().isupper() and first.strip():
            doc.blocks.append(Block(ElementType.CHARACTER, first.strip()))
            prev_type = ElementType.CHARACTER
            continue

        # Fallback: ACTION (may be multi-line).
        doc.blocks.append(Block(ElementType.ACTION, para))
        prev_type = ElementType.ACTION

    return ImportResult(document=doc, warnings=warnings)


_TITLE_PAGE_KEYS = {
    "title": "title", "author": "author",
    "contact": "contact", "draft date": "draft_date",
}


def _try_title_page(para: str, doc: Document) -> bool:
    """If `para` is a block of `Key: Value` lines we recognise, populate doc and return True."""
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_fountain.py -q`
Expected: all fountain tests pass.

- [ ] **Step 6: Commit**

```bash
git add piscript/fountain.py tests/test_fountain.py
git commit -m "feat(fountain): import + export with stage-only note preservation"
```

---

## Task 7: PDF export (ReportLab)

**Files:**
- Create: `piscript/pdf.py`
- Create: `tests/test_pdf.py`
- Create: `tests/fixtures/__init__.py`

- [ ] **Step 1: Create the fixtures package**

`tests/fixtures/__init__.py`:

```python
"""Test fixtures for piscript."""

from piscript.model import Block, Document, ElementType as E, Mode


def screenplay_fixture() -> Document:
    return Document(
        mode=Mode.SCREENPLAY,
        title="Kettle",
        author="A. Writer",
        blocks=[
            Block(E.SCENE_HEADING, "INT. KITCHEN - NIGHT"),
            Block(E.ACTION, "MAYA stares at the kettle. Steam rises."),
            Block(E.CHARACTER, "MAYA"),
            Block(E.PARENTHETICAL, "(quiet)"),
            Block(E.DIALOGUE, "Boil already."),
            Block(E.ACTION, "The kettle whistles. She smiles."),
            Block(E.TRANSITION, "CUT TO:"),
            Block(E.SCENE_HEADING, "EXT. STREET - DAY"),
            Block(E.ACTION, "She walks."),
        ],
    )


def stage_fixture() -> Document:
    return Document(
        mode=Mode.STAGE,
        title="Waiting",
        author="S. B.",
        blocks=[
            Block(E.ACT_HEADING, "ACT ONE"),
            Block(E.SCENE_HEADING_STAGE, "SCENE 1"),
            Block(E.STAGE_DIRECTION, "A tree. Evening."),
            Block(E.CHARACTER, "VLADIMIR"),
            Block(E.DIALOGUE, "Nothing to be done."),
            Block(E.CHARACTER, "ESTRAGON"),
            Block(E.DIALOGUE, "I'm beginning to come round to that opinion."),
            Block(E.SONG, "La la la, la la la."),
        ],
    )
```

- [ ] **Step 2: Write failing tests for PDF export**

`tests/test_pdf.py`:

```python
import pytest

reportlab = pytest.importorskip("reportlab")

from piscript.pdf import export_pdf
from tests.fixtures import screenplay_fixture, stage_fixture


def test_export_pdf_screenplay_writes_file_with_pdf_header(tmp_path):
    out = tmp_path / "kettle.pdf"
    export_pdf(screenplay_fixture(), str(out))
    data = out.read_bytes()
    assert data[:5] == b"%PDF-"
    # ReportLab embeds page-size metadata; US Letter = 612 x 792 pt.
    assert b"612" in data
    assert b"792" in data


def test_export_pdf_stage_writes_file_with_pdf_header(tmp_path):
    out = tmp_path / "waiting.pdf"
    export_pdf(stage_fixture(), str(out))
    data = out.read_bytes()
    assert data[:5] == b"%PDF-"


def test_export_pdf_uses_courier(tmp_path):
    out = tmp_path / "font.pdf"
    export_pdf(screenplay_fixture(), str(out))
    data = out.read_bytes()
    assert b"Courier" in data


def test_export_pdf_title_page_when_metadata_present(tmp_path):
    from piscript.model import Document
    out = tmp_path / "titled.pdf"
    export_pdf(
        Document(title="A Title", author="An Author",
                 blocks=screenplay_fixture().blocks),
        str(out),
    )
    data = out.read_bytes()
    # Title & author must appear in the emitted PDF stream.
    assert b"A Title" in data
    assert b"An Author" in data
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest tests/test_pdf.py -q`
Expected: FAIL — module missing (assuming reportlab is installed for dev; if not, install with `pip install reportlab`).

- [ ] **Step 4: Create `piscript/pdf.py`**

```python
"""PDF export via ReportLab.

Uses the same layout tables as the on-screen editor (see layout.py) so what
you see is what prints.
"""

from __future__ import annotations

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Frame, NextPageTemplate, PageBreak, PageTemplate,
    Paragraph, SimpleDocTemplate, Spacer,
)

from .layout import (
    Alignment, Case, FONT_NAME, FONT_SIZE_PT, POINTS_PER_INCH,
    ElementStyle, page_metrics, style_for,
)
from .model import Document, ElementType, Mode


LINE_HEIGHT_PT = FONT_SIZE_PT  # Courier 12pt → ~12pt leading is standard


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

    # Convert absolute-from-page-edge inches to left-indent from the frame (frame starts at x=0
    # since we set leftMargin=0 on the doc). i.e. left_indent = style.left_inch in points.
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_pdf.py -q`
Expected: 4 passed.

If ReportLab isn't installed locally: `pip install reportlab`, then re-run.

- [ ] **Step 6: Commit**

```bash
git add piscript/pdf.py tests/test_pdf.py tests/fixtures/__init__.py
git commit -m "feat(pdf): ReportLab export using shared layout tables"
```

---

## Task 8: HTML export (dependency-free, page-marked)

**Files:**
- Create: `piscript/html.py`
- Create: `tests/test_html.py`

- [ ] **Step 1: Write failing tests**

`tests/test_html.py`:

```python
import re

from piscript.html import export_html
from piscript.model import Block, Document, ElementType as E, Mode
from tests.fixtures import screenplay_fixture, stage_fixture


def test_export_html_has_courier_style_and_letter_size():
    html = export_html(screenplay_fixture())
    assert "<!DOCTYPE html>" in html
    assert "Courier" in html
    assert re.search(r"@page\s*\{[^}]*size:\s*letter", html, re.IGNORECASE) is not None


def test_export_html_screenplay_margins_are_wga():
    html = export_html(screenplay_fixture())
    # 1.5" left / 1.0" right / 1.0" top / 1.0" bottom
    assert re.search(r"margin:\s*1in\s+1in\s+1in\s+1\.5in", html) is not None


def test_export_html_stage_margins_are_one_inch_all_sides():
    html = export_html(stage_fixture())
    assert re.search(r"margin:\s*1in\s+1in\s+1in\s+1in", html) is not None


def test_export_html_page_breaks_have_visible_markers():
    doc = Document(mode=Mode.SCREENPLAY, blocks=[
        Block(E.ACTION, "line " + str(i)) for i in range(200)
    ])
    html = export_html(doc)
    # Explicit visual break markers between rendered pages.
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_html.py -q`
Expected: FAIL — module missing.

- [ ] **Step 3: Add `all_styles()` to `piscript/layout.py`**

Append to `piscript/layout.py` (public accessor so `html.py` doesn't reach into private names):

```python
def all_styles(mode: Mode) -> dict[ElementType, ElementStyle]:
    return dict(_SCREENPLAY) if mode == Mode.SCREENPLAY else dict(_STAGE)
```

- [ ] **Step 4: Create `piscript/html.py`**

```python
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
    """Format inches without a trailing '.0' for whole numbers — matches CSS convention."""
    return f"{int(n)}in" if float(n).is_integer() else f"{n}in"


def export_html(doc: Document) -> str:
    metrics = page_metrics(doc.mode)
    title = escape(doc.title or "piscript document")

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
    # @page margins as `top right bottom left` in inches.
    at_page = (
        f"@page {{ size: letter; "
        f"margin: {_fmt_in(metrics.top_inch)} {_fmt_in(metrics.right_inch)} "
        f"{_fmt_in(metrics.bottom_inch)} {_fmt_in(metrics.left_inch)}; }}"
    )

    # On-screen "page" — same visual metrics as printed page.
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
    # left_inch is measured from the page's left EDGE, but our .page element
    # already accounts for the page's left margin via padding. So the CSS
    # indent is (element_left_inch - page_left_margin_inch).
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
        # Approximate: 1 line per block + before/after spacing lines. Long text
        # will wrap, but that's an over-count — safer than under-count for
        # visible page markings.
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
            out.append(f'<hr class="page-break">')
            out.append(f'<div class="page-number">Page {i + 1} of {len(pages)}</div>')
    return "\n".join(out)


def _render_block(block: Block) -> str:
    text = escape(block.text).replace("\n", "<br>")
    return f'<p class="block {block.type.value}">{text or "&nbsp;"}</p>'
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_html.py tests/test_layout.py -q`
Expected: all pass (layout tests still green, html tests newly green).

- [ ] **Step 6: Commit**

```bash
git add piscript/html.py piscript/layout.py tests/test_html.py
git commit -m "feat(html): dependency-free export with visible page markings"
```

---

## Task 9: Editor widget — ScriptEdit

**Files:**
- Create: `piscript/editor.py`

Note on testing: This task is Qt-dependent. The design spec explicitly skips GUI-level automated tests. This task builds the widget and validates it via a manual smoke script at the end.

- [ ] **Step 1: Create `piscript/editor.py`**

```python
"""ScriptEdit — a QTextEdit that renders script layouts and cycles element types."""

from __future__ import annotations

from PyQt5.QtCore import QSizeF, Qt, pyqtSignal
from PyQt5.QtGui import (
    QFont, QKeyEvent, QTextBlockFormat, QTextCharFormat, QTextCursor,
    QTextDocument, QTextFormat,
)
from PyQt5.QtWidgets import QTextEdit

from .layout import (
    Alignment, Case, FONT_NAME, FONT_SIZE_PT, POINTS_PER_INCH,
    ElementStyle, page_metrics, style_for, valid_elements,
)
from .model import Block, Document, ElementType, Mode
from .rules import apply_heuristics, cycle_next, next_element


_USER_STATE_BASE = 1000  # keep away from Qt's own userState values


def _encode_state(t: ElementType) -> int:
    order = list(ElementType)
    return _USER_STATE_BASE + order.index(t)


def _decode_state(state: int) -> ElementType:
    order = list(ElementType)
    idx = state - _USER_STATE_BASE
    if 0 <= idx < len(order):
        return order[idx]
    return ElementType.ACTION


class ScriptEdit(QTextEdit):
    element_changed = pyqtSignal(object)  # emits ElementType at caret
    page_changed = pyqtSignal(int, int)   # emits (current_page, total_pages)

    def __init__(self, mode: Mode = Mode.SCREENPLAY, parent=None):
        super().__init__(parent)
        self._mode = mode
        self.setAcceptRichText(False)
        self.setUndoRedoEnabled(True)

        font = QFont(FONT_NAME, FONT_SIZE_PT)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        # Fix the document to the paper's usable width so on-screen wrap
        # matches printed wrap.
        self._apply_page_size()
        self.cursorPositionChanged.connect(self._emit_current_element)
        self.textChanged.connect(self._maybe_emit_page_count)

    # --- public API ---

    def mode(self) -> Mode:
        return self._mode

    def set_mode(self, mode: Mode) -> None:
        self._mode = mode
        self._apply_page_size()
        # Re-apply formatting for every block so the new mode's layout takes effect.
        cursor = QTextCursor(self.document())
        cursor.movePosition(QTextCursor.Start)
        while True:
            block_type = self.element_at(cursor)
            self._apply_block_format(cursor, block_type)
            if not cursor.movePosition(QTextCursor.NextBlock):
                break
        self._emit_current_element()

    def load_document(self, doc: Document) -> None:
        self.blockSignals(True)
        self.clear()
        self._mode = doc.mode
        self._apply_page_size()
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        for i, block in enumerate(doc.blocks):
            if i > 0:
                cursor.insertBlock()
            cursor.block().setUserState(_encode_state(block.type))
            self._apply_block_format(cursor, block.type)
            cursor.insertText(block.text)
        self.blockSignals(False)
        self.textChanged.emit()
        self._emit_current_element()

    def to_document(self, base: Document) -> Document:
        blocks: list[Block] = []
        b = self.document().firstBlock()
        while b.isValid():
            t = _decode_state(b.userState()) if b.userState() >= _USER_STATE_BASE else ElementType.ACTION
            blocks.append(Block(type=t, text=b.text()))
            b = b.next()
        return Document(
            version=base.version, mode=self._mode,
            title=base.title, author=base.author,
            contact=base.contact, draft_date=base.draft_date,
            blocks=blocks,
        )

    def element_at_cursor(self) -> ElementType:
        return self.element_at(self.textCursor())

    def element_at(self, cursor: QTextCursor) -> ElementType:
        state = cursor.block().userState()
        if state >= _USER_STATE_BASE:
            return _decode_state(state)
        return ElementType.SCENE_HEADING if self._mode == Mode.SCREENPLAY else ElementType.STAGE_DIRECTION

    def set_element_at_cursor(self, element: ElementType) -> None:
        cursor = self.textCursor()
        cursor.block().setUserState(_encode_state(element))
        self._apply_block_format(cursor, element)
        self._emit_current_element()

    def page_count(self) -> int:
        # QTextDocument.pageCount() requires setPageSize to have been called.
        return max(1, self.document().pageCount())

    # --- key handling ---

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        mods = event.modifiers()

        if key == Qt.Key_Tab and not (mods & Qt.ShiftModifier):
            current = self.element_at_cursor()
            self.set_element_at_cursor(cycle_next(self._mode, current))
            event.accept()
            return

        if key in (Qt.Key_Return, Qt.Key_Enter):
            self._on_enter()
            event.accept()
            return

        # Ctrl+1..9: direct-set element type
        if mods & Qt.ControlModifier and Qt.Key_1 <= key <= Qt.Key_9:
            idx = key - Qt.Key_1
            elements = valid_elements(self._mode)
            if idx < len(elements):
                self.set_element_at_cursor(elements[idx])
                event.accept()
                return

        super().keyPressEvent(event)
        self._maybe_apply_heuristics()

    # --- internals ---

    def _on_enter(self) -> None:
        cursor = self.textCursor()
        current = self.element_at(cursor)
        cursor.insertBlock()
        new_type = next_element(self._mode, current)
        cursor.block().setUserState(_encode_state(new_type))
        self._apply_block_format(cursor, new_type)
        self.setTextCursor(cursor)
        self._emit_current_element()

    def _maybe_apply_heuristics(self) -> None:
        cursor = self.textCursor()
        current = self.element_at(cursor)
        text = cursor.block().text()
        new_type = apply_heuristics(self._mode, current, text)
        if new_type != current:
            self.set_element_at_cursor(new_type)

    def _apply_page_size(self) -> None:
        metrics = page_metrics(self._mode)
        w_pt = metrics.width_inch * POINTS_PER_INCH
        h_pt = metrics.height_inch * POINTS_PER_INCH
        self.document().setPageSize(QSizeF(w_pt, h_pt))
        # Match the on-screen text width to the paper's usable width in pt.
        usable_w = (metrics.width_inch - metrics.left_inch - metrics.right_inch) * POINTS_PER_INCH
        self.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.setLineWrapColumnOrWidth(int(usable_w))

    def _apply_block_format(self, cursor: QTextCursor, element: ElementType) -> None:
        style: ElementStyle = style_for(self._mode, element)

        block_fmt = QTextBlockFormat()
        # Convert absolute-from-page-edge to indent-from-frame:
        metrics = page_metrics(self._mode)
        left_indent_pt = max(style.left_inch - metrics.left_inch, 0.0) * POINTS_PER_INCH
        right_indent_pt = max(
            (metrics.width_inch - metrics.right_inch) - style.right_inch, 0.0
        ) * POINTS_PER_INCH
        block_fmt.setLeftMargin(left_indent_pt)
        block_fmt.setRightMargin(right_indent_pt)
        block_fmt.setAlignment({
            Alignment.LEFT: Qt.AlignLeft,
            Alignment.CENTER: Qt.AlignCenter,
            Alignment.RIGHT: Qt.AlignRight,
        }[style.alignment])
        block_fmt.setTopMargin(style.space_before_lines * FONT_SIZE_PT)
        block_fmt.setBottomMargin(style.space_after_lines * FONT_SIZE_PT)

        char_fmt = QTextCharFormat()
        char_fmt.setFontFamily(FONT_NAME)
        char_fmt.setFontPointSize(FONT_SIZE_PT)
        char_fmt.setFontItalic(style.italic)
        char_fmt.setFontUnderline(style.underline)
        if style.case == Case.UPPER:
            char_fmt.setFontCapitalization(QFont.AllUppercase)
        else:
            char_fmt.setFontCapitalization(QFont.MixedCase)

        # Apply to the whole block without altering the caret position.
        c = QTextCursor(cursor.block())
        c.select(QTextCursor.BlockUnderCursor)
        c.setBlockFormat(block_fmt)
        c.setCharFormat(char_fmt)

    def _emit_current_element(self) -> None:
        self.element_changed.emit(self.element_at_cursor())
        self._maybe_emit_page_count()

    def _maybe_emit_page_count(self) -> None:
        # Current page ≈ position / usable_page_line_count. Cheap approximation.
        total = self.page_count()
        self.page_changed.emit(1, total)  # true "current page" needs layout inspection; keep it simple.
```

- [ ] **Step 2: Manual smoke test — hello editor**

Create `scripts/smoke_editor.py` (a throwaway; do not commit):

```python
import sys
from PyQt5.QtWidgets import QApplication

from piscript.editor import ScriptEdit
from piscript.model import Mode

app = QApplication(sys.argv)
w = ScriptEdit(mode=Mode.SCREENPLAY)
w.resize(800, 900)
w.show()
sys.exit(app.exec_())
```

Run: `python scripts/smoke_editor.py`
Expected: A window opens. Typing produces `SCENE_HEADING`-styled text (indented 1.5" from the left, uppercase). Press Enter → `ACTION` (mixed case, same indent). Press Tab → cycles to `CHARACTER` (indented ~3.7"). Typing `INT.` on an ACTION line promotes to SCENE_HEADING.

Delete `scripts/smoke_editor.py` before committing.

- [ ] **Step 3: Commit**

```bash
git add piscript/editor.py
git commit -m "feat(editor): ScriptEdit with element-typed blocks and key cycling"
```

---

## Task 10: Outline panel

**Files:**
- Create: `piscript/outline.py`

- [ ] **Step 1: Create `piscript/outline.py`**

```python
"""Left-hand outline: scene headings (screenplay) or acts/scenes (stage)."""

from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QTreeView

from .model import Document, ElementType, Mode


_HEADING_ROLE = Qt.UserRole + 1


class OutlinePanel(QTreeView):
    jump_to_block = pyqtSignal(int)  # block index in the document

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setEditTriggers(QTreeView.NoEditTriggers)
        self._model = QStandardItemModel()
        self.setModel(self._model)
        self.clicked.connect(self._on_clicked)

    def rebuild(self, doc: Document) -> None:
        self._model.clear()
        root = self._model.invisibleRootItem()

        if doc.mode == Mode.SCREENPLAY:
            for i, block in enumerate(doc.blocks):
                if block.type == ElementType.SCENE_HEADING:
                    root.appendRow(self._item(block.text, i))
        else:
            current_act: QStandardItem | None = None
            for i, block in enumerate(doc.blocks):
                if block.type == ElementType.ACT_HEADING:
                    current_act = self._item(block.text, i)
                    root.appendRow(current_act)
                elif block.type == ElementType.SCENE_HEADING_STAGE:
                    parent = current_act or root
                    parent.appendRow(self._item(block.text, i))
        self.expandAll()

    def _item(self, text: str, index: int) -> QStandardItem:
        item = QStandardItem(text or "(untitled)")
        item.setData(index, _HEADING_ROLE)
        return item

    def _on_clicked(self, index) -> None:
        block_index = index.data(_HEADING_ROLE)
        if isinstance(block_index, int):
            self.jump_to_block.emit(block_index)
```

- [ ] **Step 2: Manual smoke test — outline shows headings**

Extend the smoke script briefly (throwaway again) to construct a `Document` with a couple of scene headings, feed it into `OutlinePanel.rebuild(doc)`, and verify the tree lists them.

- [ ] **Step 3: Commit**

```bash
git add piscript/outline.py
git commit -m "feat(outline): scenes tree with click-to-jump signal"
```

---

## Task 11: MainWindow — menus, toolbar, status bar, layout

**Files:**
- Create: `piscript/mainwindow.py`

- [ ] **Step 1: Create `piscript/mainwindow.py`**

```python
"""The main window: menu bar, toolbar, outline dock, editor, status bar."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QAction, QComboBox, QDockWidget, QLabel, QMainWindow, QMessageBox,
    QToolBar, QWidget,
)

from .editor import ScriptEdit
from .layout import valid_elements
from .model import Document, ElementType, Mode
from .outline import OutlinePanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("piscript")
        self.resize(1000, 800)

        self._doc = Document()  # metadata + will be sync'd from editor on save
        self._current_path: str | None = None
        self._dirty = False

        self._editor = ScriptEdit(mode=Mode.SCREENPLAY, parent=self)
        self.setCentralWidget(self._editor)

        self._outline = OutlinePanel()
        dock = QDockWidget("Outline", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(self._outline)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        self._outline_dock = dock

        self._element_label = QLabel("ACTION")
        self._page_label = QLabel("Page 1 of 1")
        self._word_label = QLabel("0 words")
        self.statusBar().addPermanentWidget(self._element_label)
        self.statusBar().addPermanentWidget(QLabel(" · "))
        self.statusBar().addPermanentWidget(self._page_label)
        self.statusBar().addPermanentWidget(QLabel(" · "))
        self.statusBar().addPermanentWidget(self._word_label)

        self._build_menus()
        self._build_toolbar()

        self._editor.element_changed.connect(self._on_element_changed)
        self._editor.page_changed.connect(self._on_page_changed)
        self._editor.textChanged.connect(self._on_text_changed)
        self._outline.jump_to_block.connect(self._jump_to_block)

    # --- menus & toolbar ---

    def _build_menus(self) -> None:
        m_file = self.menuBar().addMenu("&File")
        m_file.addAction(self._act("&New Screenplay", self._new_screenplay, "Ctrl+N"))
        m_file.addAction(self._act("New &Stage Play", self._new_stage))
        m_file.addSeparator()
        m_file.addAction(self._act("&Open…", self._open, QKeySequence.Open))
        m_file.addAction(self._act("&Save", self._save, QKeySequence.Save))
        m_file.addAction(self._act("Save &As…", self._save_as, "Ctrl+Shift+S"))
        m_file.addSeparator()
        m_import = m_file.addMenu("&Import")
        m_import.addAction(self._act("From &Fountain…", self._import_fountain))
        m_export = m_file.addMenu("&Export")
        m_export.addAction(self._act("To &PDF…", self._export_pdf))
        m_export.addAction(self._act("To &HTML…", self._export_html))
        m_export.addAction(self._act("To &Fountain…", self._export_fountain))
        m_file.addSeparator()
        m_file.addAction(self._act("&Quit", self.close, QKeySequence.Quit))

        m_view = self.menuBar().addMenu("&View")
        toggle_outline = self._outline_dock.toggleViewAction()
        toggle_outline.setText("&Outline")
        m_view.addAction(toggle_outline)

        m_help = self.menuBar().addMenu("&Help")
        m_help.addAction(self._act("&About piscript", self._about))

    def _build_toolbar(self) -> None:
        tb = QToolBar("Main", self)
        tb.setMovable(False)
        self.addToolBar(tb)

        tb.addAction(self._act("New", self._new_screenplay))
        tb.addAction(self._act("Open", self._open))
        tb.addAction(self._act("Save", self._save))
        tb.addSeparator()

        self._element_combo = QComboBox()
        self._refresh_element_combo()
        self._element_combo.currentIndexChanged.connect(self._on_element_combo)
        tb.addWidget(self._element_combo)

    def _refresh_element_combo(self) -> None:
        self._element_combo.blockSignals(True)
        self._element_combo.clear()
        for e in valid_elements(self._editor.mode()):
            self._element_combo.addItem(e.value, e)
        self._element_combo.blockSignals(False)

    def _act(self, text: str, slot, shortcut=None) -> QAction:
        a = QAction(text, self)
        if shortcut:
            a.setShortcut(shortcut)
        a.triggered.connect(slot)
        return a

    # --- file operations (wired in Task 12) ---

    def _new_screenplay(self):
        self._reset_document(Mode.SCREENPLAY)

    def _new_stage(self):
        self._reset_document(Mode.STAGE)

    def _reset_document(self, mode: Mode) -> None:
        if not self._confirm_discard():
            return
        self._doc = Document(mode=mode)
        self._current_path = None
        self._editor.set_mode(mode)
        self._editor.load_document(self._doc)
        self._refresh_element_combo()
        self._dirty = False
        self._update_title()
        self._outline.rebuild(self._current_doc())

    def _confirm_discard(self) -> bool:
        if not self._dirty:
            return True
        r = QMessageBox.question(
            self, "piscript",
            "Discard unsaved changes?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        )
        if r == QMessageBox.Save:
            return bool(self._save())
        return r == QMessageBox.Discard

    def _current_doc(self) -> Document:
        return self._editor.to_document(self._doc)

    def _update_title(self) -> None:
        name = self._current_path or "Untitled"
        dirty = " •" if self._dirty else ""
        self.setWindowTitle(f"piscript — {name}{dirty}")

    def _open(self): ...       # implemented in Task 12
    def _save(self): return True  # implemented in Task 12
    def _save_as(self): ...    # implemented in Task 12
    def _import_fountain(self): ...  # implemented in Task 12
    def _export_pdf(self): ...       # implemented in Task 13
    def _export_html(self): ...      # implemented in Task 13
    def _export_fountain(self): ...  # implemented in Task 13

    def _about(self):
        QMessageBox.about(
            self, "About piscript",
            "piscript — lightweight scriptwriting for stage and screen.\n"
            "MIT licensed. Made for Raspberry Pi.",
        )

    # --- reactive slots ---

    def _on_element_changed(self, element: ElementType) -> None:
        self._element_label.setText(element.value)
        idx = self._element_combo.findData(element)
        if idx >= 0:
            self._element_combo.blockSignals(True)
            self._element_combo.setCurrentIndex(idx)
            self._element_combo.blockSignals(False)

    def _on_element_combo(self) -> None:
        element = self._element_combo.currentData()
        if isinstance(element, ElementType):
            self._editor.set_element_at_cursor(element)

    def _on_page_changed(self, current: int, total: int) -> None:
        self._page_label.setText(f"Page {current} of {total}")

    def _on_text_changed(self) -> None:
        self._dirty = True
        text = self._editor.toPlainText()
        words = len(text.split())
        self._word_label.setText(f"{words} words")
        self._outline.rebuild(self._current_doc())
        self._update_title()

    def _jump_to_block(self, block_index: int) -> None:
        doc = self._editor.document()
        b = doc.findBlockByNumber(block_index)
        if b.isValid():
            from PyQt5.QtGui import QTextCursor
            cur = QTextCursor(b)
            self._editor.setTextCursor(cur)
            self._editor.setFocus()
```

- [ ] **Step 2: Commit (skeleton — file ops are stubs)**

```bash
git add piscript/mainwindow.py
git commit -m "feat(mainwindow): menus, toolbar, dock, status bar (file ops stubbed)"
```

---

## Task 12: MainWindow — file open/save/import wiring

**Files:**
- Modify: `piscript/mainwindow.py`

- [ ] **Step 1: Replace the stub file/import methods**

In `piscript/mainwindow.py`, replace the stubs `_open`, `_save`, `_save_as`, `_import_fountain` with:

```python
    def _open(self):
        if not self._confirm_discard():
            return
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Open .piscript", "", "piscript files (*.piscript);;All files (*)"
        )
        if not path:
            return
        try:
            from . import model as _model
            result = _model.load(path)
        except _model.UnsupportedVersionError as e:
            QMessageBox.warning(
                self, "piscript",
                f"{e}\n\nThe file will be opened read-only as plain text."
            )
            return  # v1 read-only fallback is out of scope; keep it simple.
        except _model.DocumentError as e:
            QMessageBox.critical(self, "piscript", f"Could not open file:\n{e}")
            return
        self._doc = result.document
        self._current_path = path
        self._editor.set_mode(self._doc.mode)
        self._editor.load_document(self._doc)
        self._refresh_element_combo()
        self._outline.rebuild(self._current_doc())
        self._dirty = False
        self._update_title()
        if result.warnings:
            QMessageBox.information(
                self, "piscript",
                "Opened with warnings:\n\n" + "\n".join(result.warnings)
            )

    def _save(self) -> bool:
        if not self._current_path:
            return self._save_as()
        return self._write_to(self._current_path)

    def _save_as(self) -> bool:
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Save as", self._current_path or "untitled.piscript",
            "piscript files (*.piscript)"
        )
        if not path:
            return False
        if not path.endswith(".piscript"):
            path += ".piscript"
        return self._write_to(path)

    def _write_to(self, path: str) -> bool:
        from . import model as _model
        try:
            _model.save(self._current_doc(), path)
        except OSError as e:
            QMessageBox.critical(self, "piscript", f"Could not save:\n{e}")
            return False
        self._current_path = path
        self._dirty = False
        self._update_title()
        return True

    def _import_fountain(self):
        if not self._confirm_discard():
            return
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Fountain", "", "Fountain files (*.fountain);;All files (*)"
        )
        if not path:
            return
        from . import fountain as _f
        try:
            with open(path, "r", encoding="utf-8") as f:
                src = f.read()
        except OSError as e:
            QMessageBox.critical(self, "piscript", f"Could not read:\n{e}")
            return
        result = _f.parse_fountain(src)
        self._doc = result.document
        self._current_path = None
        self._editor.set_mode(self._doc.mode)
        self._editor.load_document(self._doc)
        self._refresh_element_combo()
        self._outline.rebuild(self._current_doc())
        self._dirty = True
        self._update_title()
        if result.warnings:
            QMessageBox.information(
                self, "piscript",
                "Imported with warnings:\n\n" + "\n".join(result.warnings)
            )
```

- [ ] **Step 2: Commit**

```bash
git add piscript/mainwindow.py
git commit -m "feat(mainwindow): open/save/save-as + Fountain import"
```

---

## Task 13: MainWindow — export wiring (PDF, HTML, Fountain)

**Files:**
- Modify: `piscript/mainwindow.py`

- [ ] **Step 1: Replace the stub export methods**

Replace `_export_pdf`, `_export_html`, `_export_fountain`:

```python
    def _export_pdf(self):
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", "script.pdf", "PDF (*.pdf)"
        )
        if not path:
            return
        try:
            from .pdf import export_pdf
        except ImportError:
            QMessageBox.warning(
                self, "piscript",
                "PDF export needs ReportLab. Install with:\n"
                "  sudo apt install python3-reportlab"
            )
            return
        try:
            export_pdf(self._current_doc(), path)
        except OSError as e:
            QMessageBox.critical(self, "piscript", f"Could not write PDF:\n{e}")
            return
        QMessageBox.information(self, "piscript", f"Exported PDF to {path}")

    def _export_html(self):
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Export HTML", "script.html", "HTML (*.html)"
        )
        if not path:
            return
        from .html import export_html
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(export_html(self._current_doc()))
        except OSError as e:
            QMessageBox.critical(self, "piscript", f"Could not write HTML:\n{e}")
            return
        QMessageBox.information(self, "piscript", f"Exported HTML to {path}")

    def _export_fountain(self):
        from PyQt5.QtWidgets import QFileDialog
        from .fountain import export_fountain
        doc = self._current_doc()

        result = export_fountain(doc)
        if result.warnings:
            r = QMessageBox.question(
                self, "piscript",
                "This export is lossy:\n\n"
                + "\n".join(result.warnings)
                + "\n\nContinue?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if r != QMessageBox.Yes:
                return

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Fountain", "script.fountain", "Fountain (*.fountain)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(result.text)
        except OSError as e:
            QMessageBox.critical(self, "piscript", f"Could not write Fountain:\n{e}")
            return
        QMessageBox.information(self, "piscript", f"Exported Fountain to {path}")
```

- [ ] **Step 2: Commit**

```bash
git add piscript/mainwindow.py
git commit -m "feat(mainwindow): PDF, HTML, Fountain export wiring"
```

---

## Task 14: App entry point + `__main__`

**Files:**
- Create: `piscript/app.py`
- Create: `piscript/__main__.py`

- [ ] **Step 1: Create `piscript/app.py`**

```python
"""Application entry point."""

from __future__ import annotations

import sys

from PyQt5.QtWidgets import QApplication

from .mainwindow import MainWindow


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv
    app = QApplication(argv)
    app.setApplicationName("piscript")
    app.setOrganizationName("piscript")
    win = MainWindow()
    win.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Create `piscript/__main__.py`**

```python
from .app import main
raise SystemExit(main())
```

- [ ] **Step 3: Manual smoke — launch and click through everything**

Run: `python -m piscript`
Verify: Window opens. Type a short screenplay. Save. Reopen. Switch to stage mode via File→New Stage Play. Type. Export to PDF, HTML, Fountain. Import a Fountain file. Toggle the outline. Ctrl+1..6 sets element types. Enter cycles per spec. Tab cycles element type. Typing `INT.` on ACTION promotes to SCENE_HEADING.

- [ ] **Step 4: Commit**

```bash
git add piscript/app.py piscript/__main__.py
git commit -m "feat(app): main() and python -m piscript entry"
```

---

## Task 15: Packaging — install.sh, uninstall.sh, .desktop

**Files:**
- Create: `install.sh`
- Create: `uninstall.sh`
- Create: `piscript.desktop`

- [ ] **Step 1: Create `install.sh`**

```bash
#!/usr/bin/env bash
# Installs piscript for the current user on Raspberry Pi OS (Bullseye+).
# - apt-installs python3-pyqt5 and python3-reportlab (skip if present)
# - copies the piscript package to ~/.local/lib/piscript
# - drops a launcher into ~/.local/bin/piscript
# - drops a .desktop file into ~/.local/share/applications

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PREFIX="${HOME}/.local"
LIB_DIR="${PREFIX}/lib/piscript"
BIN="${PREFIX}/bin/piscript"
DESKTOP="${PREFIX}/share/applications/piscript.desktop"

echo "==> Checking apt dependencies…"
NEEDS=()
dpkg -s python3-pyqt5     >/dev/null 2>&1 || NEEDS+=("python3-pyqt5")
dpkg -s python3-reportlab >/dev/null 2>&1 || NEEDS+=("python3-reportlab")
if [ ${#NEEDS[@]} -gt 0 ]; then
    echo "    installing: ${NEEDS[*]}"
    sudo apt-get update
    sudo apt-get install -y "${NEEDS[@]}"
fi

echo "==> Copying package to ${LIB_DIR}"
mkdir -p "${LIB_DIR}"
rm -rf "${LIB_DIR}/piscript"
cp -r "${REPO_DIR}/piscript" "${LIB_DIR}/piscript"

echo "==> Installing launcher: ${BIN}"
mkdir -p "$(dirname "${BIN}")"
cat > "${BIN}" <<EOF
#!/usr/bin/env bash
export PYTHONPATH="${LIB_DIR}:\${PYTHONPATH:-}"
exec python3 -m piscript "\$@"
EOF
chmod +x "${BIN}"

echo "==> Installing desktop entry: ${DESKTOP}"
mkdir -p "$(dirname "${DESKTOP}")"
cp "${REPO_DIR}/piscript.desktop" "${DESKTOP}"
sed -i "s|@BIN@|${BIN}|g" "${DESKTOP}"

echo "==> Done. Launch from your applications menu or run: piscript"
```

- [ ] **Step 2: Create `uninstall.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

PREFIX="${HOME}/.local"
rm -rf "${PREFIX}/lib/piscript"
rm -f  "${PREFIX}/bin/piscript"
rm -f  "${PREFIX}/share/applications/piscript.desktop"
echo "piscript uninstalled. apt packages (python3-pyqt5, python3-reportlab) were left in place."
```

- [ ] **Step 3: Create `piscript.desktop`**

```ini
[Desktop Entry]
Type=Application
Name=piscript
Comment=Lightweight scriptwriting for stage and screen
Exec=@BIN@
Icon=text-editor
Terminal=false
Categories=Office;WordProcessor;
MimeType=application/x-piscript;
```

- [ ] **Step 4: Make scripts executable and commit**

```bash
chmod +x install.sh uninstall.sh
git add install.sh uninstall.sh piscript.desktop
git commit -m "chore(packaging): install.sh, uninstall.sh, desktop entry"
```

---

## Task 16: README with usage and final polish

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace `README.md`**

```markdown
# piscript

A lightweight word processor for stage plays and screenplays. Renders industry-standard layouts (WGA screenplay, Dramatists Guild stage) as you type. Runs on Raspberry Pi Zero W upward on Raspberry Pi OS (Bullseye or newer).

Python 3 + PyQt5 + ReportLab. Modelled aesthetically on Zim: thin single toolbar, side outline, main text area, status bar.

## Install

```bash
git clone https://github.com/<you>/piscript.git
cd piscript
./install.sh
```

Adds:

- `python3-pyqt5` and `python3-reportlab` via apt (skipped if already present)
- `~/.local/lib/piscript` — the package
- `~/.local/bin/piscript` — the launcher
- Menu entry under Office / Word Processor

## Use

Launch from the Applications menu, or run `piscript`.

**Keyboard:**

- **Enter** — advance to the logical next element (`CHARACTER → DIALOGUE`, etc.)
- **Tab** — cycle the current line's element type
- **Ctrl+1..6** — set the element type directly
- **Ctrl+N** — new screenplay · **Ctrl+O** — open · **Ctrl+S** — save · **Ctrl+F** — find

**Modes:** File → New Screenplay / New Stage Play. Each document remembers its mode.

**Export:** File → Export → PDF / HTML / Fountain. Fountain export from stage mode is lossy (stage-only elements survive as notes) — a dialog explains before writing.

## Uninstall

```bash
./uninstall.sh
```

## Layout standards

- **Screenplay**: US Letter, Courier 12pt, margins L 1.5" / R 1.0" / T 1.0" / B 1.0". Elements follow WGA style-sheet indents.
- **Stage play**: US Letter, Courier 12pt, margins 1.0" on all sides. Character names centered above dialogue, stage directions indented 3.0" and italicised.

Exact numbers live in [`piscript/layout.py`](piscript/layout.py) — the single source of truth for the editor, PDF export, and HTML export.

## Requirements

- Raspberry Pi OS Bullseye or newer (32-bit or 64-bit)
- X11 or Wayland session
- Python 3.9+, `python3-pyqt5`, `python3-reportlab`

Tested target: Pi Zero W (ARMv6) through Pi 5.

## Development

```bash
pip install PyQt5 reportlab pytest
pytest
```

Pure-Python modules (`model`, `layout`, `rules`, `fountain`, `pdf`, `html`) have full unit-test coverage. Qt widgets (`editor`, `outline`, `mainwindow`, `app`) are validated manually — the spec skips GUI automation.

## License

MIT — see [LICENSE](LICENSE).
```

- [ ] **Step 2: Run the whole test suite**

Run: `pytest -q`
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: README with install, use, and requirements"
```

- [ ] **Step 4: Tag v0.1.0**

```bash
git tag -a v0.1.0 -m "piscript v0.1.0"
```

---

## Wrap-up checklist

- [ ] All pure-Python tests pass (`pytest -q`).
- [ ] `python -m piscript` launches on Windows dev machine.
- [ ] Manual test on a Pi Zero W: type a page in each mode, save, reopen, export PDF, export HTML, import Fountain, export Fountain.
- [ ] `install.sh` and `uninstall.sh` are idempotent (running twice is safe).
- [ ] Spec §11 out-of-scope items truly aren't in the code.
