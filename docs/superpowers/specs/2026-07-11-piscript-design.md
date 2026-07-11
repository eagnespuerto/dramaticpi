# piscript — lightweight scriptwriting for Raspberry Pi

**Status:** Design (2026-07-11)
**Target platform:** Raspberry Pi OS (Bullseye or newer), 32-bit or 64-bit, Pi Zero W (ARMv6, 512 MB RAM) and up.

## 1. Purpose

A minimal word processor for stage plays and screenplays that renders industry-standard layouts as you type. Runs comfortably on a Pi Zero W. Ships as a Python 3 + PyQt5 desktop app installed by a shell script — the same house style as the sibling project `pinight`.

Non-goals: collaboration, cloud sync, revision-marking, storyboard/index-card views, dark mode / theming, dictation, mobile.

## 2. UX conventions

Interface aesthetic modelled on **Zim** (the desktop wiki): thin single toolbar, left side-panel for document outline, main text area, status bar. No animations, no ribbons, no theming controls, no dockable panels.

- **Menu bar**: File / Edit / Format / View / Help.
- **Toolbar**: New / Open / Save / Export ▾ / element-type dropdown / a hard divider / find.
- **Left panel (Outline)**: a `QTreeView` listing scene headings (screenplay) or acts+scenes (stage). Click to jump the caret. Toggle-hide via View menu.
- **Main area**: one `QTextEdit` styled to render the current mode's layout at the actual paper metrics (see §5).
- **Status bar**: current element type · page N of M · word count.

Keyboard is the primary interaction model:

- **Enter** advances to the logical next element for the current mode (see §6).
- **Tab** cycles the current line's element type.
- **Ctrl+1..9** sets the current line's element type explicitly.
- **Ctrl+S / Ctrl+O / Ctrl+N / Ctrl+P / Ctrl+F** as expected.

## 3. Supported layout standards

Encoded per the **WGA screenplay format** and the **Dramatists Guild** / Samuel French stage convention. Exact numbers below are treated as the ground truth by both the editor renderer and the PDF/HTML exporters.

### 3.1 Screenplay mode (US industry standard)

- Paper: US Letter, 8.5" × 11".
- Font: **Courier 12 pt** (Courier Prime or Courier New at 12 pt — 10 chars/inch, 6 lines/inch).
- Margins: **Left 1.5", Right 1.0", Top 1.0", Bottom 1.0"**.
- Element left-indents (measured from the paper's left edge) and right margins:

  | Element         | Left edge | Right edge | Case      | Alignment |
  |-----------------|-----------|------------|-----------|-----------|
  | Scene heading   | 1.5"      | 7.5"       | UPPERCASE | left      |
  | Action          | 1.5"      | 7.5"       | mixed     | left      |
  | Character       | 3.7"      | 7.5"       | UPPERCASE | left      |
  | Parenthetical   | 3.1"      | 5.5"       | mixed     | left      |
  | Dialogue        | 2.5"      | 6.0"       | mixed     | left      |
  | Transition      | 1.5"      | 7.5"       | UPPERCASE | right     |

- One printed page ≈ 55 lines of body text, ≈ one minute of screen time.

### 3.2 Stage-play mode (Samuel French / Dramatists Guild)

- Paper: US Letter, 8.5" × 11".
- Font: **Courier 12 pt**.
- Margins: **1.0" on all four sides**.
- Element rules:

  | Element (enum)                | Rendering                                                     |
  |-------------------------------|---------------------------------------------------------------|
  | Act heading (`ACT_HEADING`)   | Centered, UPPERCASE, underlined, extra blank line after       |
  | Scene heading (`SCENE_HEADING_STAGE`) | Centered, UPPERCASE, one blank line after            |
  | Character (`CHARACTER`)       | Centered, UPPERCASE, on its own line                          |
  | Dialogue (`DIALOGUE`)         | Full-width (1.0" both sides)                                  |
  | Stage direction (`STAGE_DIRECTION`) | Indented 3.0" from left, italic where possible, or in parens |
  | Song / lyric (`SONG`)         | Indented 1.5", italic                                         |

Note: screenplay `SCENE_HEADING` and stage `SCENE_HEADING_STAGE` are distinct enum values because they render differently (left-aligned uppercase vs. centered uppercase). Screenplay and stage modes share `CHARACTER` and `DIALOGUE` enum values — a mode-aware layout table renders them differently.

- No page-per-minute convention.

## 4. File formats

### 4.1 Native: `.piscript` (JSON, UTF-8)

```json
{
  "version": 1,
  "mode": "screenplay",
  "title": "Untitled",
  "author": "",
  "contact": "",
  "draft_date": "",
  "blocks": [
    { "type": "SCENE_HEADING", "text": "INT. KITCHEN - NIGHT" },
    { "type": "ACTION",        "text": "MAYA stares at the kettle." },
    { "type": "CHARACTER",     "text": "MAYA" },
    { "type": "DIALOGUE",      "text": "Boil already." }
  ]
}
```

Rules:

- `version` is an integer; loader raises on unknown future versions and offers read-only text open.
- `mode` is `"screenplay"` or `"stage"`; unknown values coerce to `"screenplay"` and warn.
- Unknown `type` values coerce to `"ACTION"` and warn.
- No embedded formatting. The element type is the semantic; presentation is derived from `mode` × `type` via §3 tables.
- Blocks preserve source order. Blank blocks are permitted.

### 4.2 Optional import/export: Fountain (`.fountain`)

Menu items **File → Import Fountain…** and **File → Export Fountain…**. Best-effort:

- Screenplay elements map cleanly to Fountain's spec.
- Stage-only elements (`ACT_HEADING`, `SCENE_HEADING_STAGE`, `SONG`, `STAGE_DIRECTION`) export as Fountain notes (`[[ … ]]`) with a comment marking the original type, and a dialog on export warns about lossy conversion.
- Fountain import: elements not recognised become `ACTION` with a warning banner listing line numbers.

### 4.3 Export: PDF (via ReportLab)

Menu item **File → Export → PDF…**. Uses `python3-reportlab` (apt). One `SimpleDocTemplate` with a mode-specific `PageTemplate`; each block becomes a `Paragraph` with a `ParagraphStyle` derived from the same §3 tables. Optional title page as a separate `Frame`. Missing ReportLab at export time surfaces a dialog pointing to `sudo apt install python3-reportlab` — no crash.

### 4.4 Export: HTML (page-marked, dependency-free)

Menu item **File → Export → HTML…**. Single self-contained `.html` file:

- Inline `<style>` with `@page { size: letter; margin: … }` for print, and screen CSS that renders the layout at the correct fixed-width Courier metrics.
- Explicit `<hr class="page-break">` between paginated pages so page ends are visible on-screen even without Print Preview; a small `<div class="page-number">` at each break shows "Page N".
- No external assets, no JavaScript. Ships as a single file; deps: none.

## 5. Editor rendering strategy

One `QTextEdit`. Each paragraph is a `QTextBlock`; its `userState` stores the element type enum. The editor keeps a `QTextDocument` whose page metric matches §3 exactly (Courier 12 pt sizing, paper width, margin frames) so on-screen text wraps at the same column as printed output — a WYSIWYG guarantee.

Applying a block's element type re-applies its `QTextBlockFormat` (left/right indents in points, alignment) and `QTextCharFormat` (font, case-transform via QTextCharFormat.setFontCapitalization for CHARACTER/SCENE_HEADING/etc.). No custom paint code; QTextEdit paints only visible lines, so performance stays flat as documents grow.

Page numbering for the status bar is computed from `QTextDocument`'s `pageCount()` with the mode's paper metrics applied to the document.

## 6. Element transition rules

Stored in `rules.py` as two dispatch tables, one per mode.

### 6.1 Screenplay

- **Enter next** (element after pressing Enter on a non-empty line):
  `SCENE_HEADING → ACTION`
  `ACTION → ACTION`
  `CHARACTER → DIALOGUE`
  `DIALOGUE → ACTION`
  `PARENTHETICAL → DIALOGUE`
  `TRANSITION → SCENE_HEADING`
- **Tab cycle**: `SCENE_HEADING → ACTION → CHARACTER → PARENTHETICAL → DIALOGUE → TRANSITION → SCENE_HEADING`.
- **Ctrl+1..6** direct set (in the same order as Tab cycle).
- **Auto-heuristics on Enter into an empty line**: if the previous line was empty and the user types `INT.`/`EXT.`/`I/E.` (case-insensitive) at start-of-line, promote to `SCENE_HEADING`. If they type a `(`, promote to `PARENTHETICAL`.

### 6.2 Stage

- **Enter next**:
  `ACT_HEADING → SCENE_HEADING_STAGE`
  `SCENE_HEADING_STAGE → STAGE_DIRECTION`
  `STAGE_DIRECTION → CHARACTER`
  `CHARACTER → DIALOGUE`
  `DIALOGUE → CHARACTER` (rapid dialogue is the common case in stage plays)
  `SONG → CHARACTER`
- **Tab cycle**: `CHARACTER → DIALOGUE → STAGE_DIRECTION → SCENE_HEADING_STAGE → ACT_HEADING → SONG → CHARACTER`.
- **Ctrl+1..6** direct set.

## 7. Components

Pure-Python, no Qt imports:

- `piscript/model.py` — `Document`, `Block`, `ElementType`, `Mode`; JSON load/save; version + type coercion.
- `piscript/layout.py` — the §3 tables as data. Single source of truth consumed by editor, PDF, and HTML.
- `piscript/rules.py` — the §6 tables and heuristics.
- `piscript/fountain.py` — Fountain import/export (lossy warnings).
- `piscript/pdf.py` — ReportLab export.
- `piscript/html.py` — HTML export with page markings.

Qt-dependent:

- `piscript/editor.py` — `ScriptEdit(QTextEdit)`; applies §3 formats via §6 rules; emits `element_changed`, `page_changed` signals.
- `piscript/outline.py` — `OutlinePanel(QTreeView)`; rebuilds from document; click-to-jump.
- `piscript/mainwindow.py` — menus, toolbar, status bar, dialogs, file wiring.
- `piscript/app.py` — entry point (`main()`).

Packaging (pinight parity):

- `install.sh`, `uninstall.sh`, `piscript.desktop`, `README.md`, `LICENSE` (MIT).

## 8. Error handling

| Scenario                                         | Behaviour                                                                                       |
|--------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `.piscript` file has bad JSON                    | Dialog: "Could not parse". Offer "Open as plain text (read-only)".                              |
| `.piscript` `version` > 1                        | Dialog: "Written by a newer piscript". Offer read-only.                                         |
| Unknown `mode` value                             | Coerce to `screenplay`, non-blocking status-bar warning.                                        |
| Unknown block `type` value                       | Coerce to `ACTION`, one banner listing affected blocks.                                         |
| ReportLab missing on PDF export                  | Dialog with the apt-install command.                                                            |
| Fountain export from stage mode with stage-only elements | Dialog: "Some elements will be exported as notes and may not survive round-tripping." Offer Continue / Cancel. |
| Disk full / write failure on save                | Dialog with error; document remains dirty.                                                      |
| Unsaved changes on close                         | Standard Save / Discard / Cancel dialog.                                                        |

## 9. Testing

Pure-Python, no display required:

- `tests/test_model.py` — JSON round-trip, version coercion, unknown-type coercion, ordering.
- `tests/test_layout.py` — every number in §3 is asserted against the layout tables (regression guard against accidental format drift).
- `tests/test_rules.py` — every Enter and Tab transition in both modes; each heuristic.
- `tests/test_fountain.py` — round-trip a screenplay fixture; stage-only elements survive as notes with the expected marker.
- `tests/test_pdf.py` — export a fixture; assert `pageCount == expected` and that ReportLab's byte stream mentions the expected font, page size, and margins.
- `tests/test_html.py` — export a fixture; assert page-break count and per-page numbering, and that Courier metrics appear in the inline CSS.

No GUI automation. Manual smoke: install on a Pi Zero W, type a page in each mode, export to all three targets, reopen the `.piscript`.

## 10. Packaging & install

`install.sh`:

- `apt install -y python3-pyqt5 python3-reportlab` (skip installed ones).
- Copy the `piscript/` package to `~/.local/lib/piscript/`.
- Drop a `~/.local/bin/piscript` launcher that runs `python3 -m piscript`.
- Copy `piscript.desktop` to `~/.local/share/applications/`.

`uninstall.sh` reverses all of the above.

## 11. Out of scope

Collaboration, revision marks, storyboard/index-card views, dictation, dark mode / theming, plugin system, spellcheck, autosave, snapshots, undo history beyond Qt's built-in per-session undo, custom fonts beyond Courier, tables, images.

## 12. Open questions

None at design time. All open questions resolved during brainstorming: format scope (both stage & screenplay), UI stack (PyQt5), native format (custom JSON), exports (PDF + HTML + optional Fountain), aesthetic (Zim-like).
