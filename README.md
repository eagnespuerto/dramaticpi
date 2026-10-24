# DramaticPi

[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![release](https://img.shields.io/github/v/release/eagnespuerto/dramaticpi?include_prereleases&sort=semver)](https://github.com/eagnespuerto/dramaticpi/releases/latest)
[![made with](https://img.shields.io/badge/made%20with-Python-3776AB?logo=python&logoColor=white)](https://github.com/eagnespuerto/dramaticpi)
[![platform](https://img.shields.io/badge/platform-Raspberry%20Pi-A22846?logo=raspberrypi&logoColor=white)](https://github.com/eagnespuerto/dramaticpi#readme)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-support%20me-FF5E5B?logo=kofi&logoColor=white)](https://ko-fi.com/eagnespuerto)
[![Linktree](https://img.shields.io/badge/Linktree-soitsagnes-43E55E?logo=linktree&logoColor=white)](https://linktr.ee/soitsagnes)

A lightweight word processor for stage plays and screenplays. Renders industry-standard layouts (WGA screenplay, Dramatists Guild stage) as you type. Runs on Raspberry Pi Zero W upward on Raspberry Pi OS (Bullseye or newer).

Python 3 + PyQt5 + ReportLab. Modelled aesthetically on Zim: thin single toolbar, side outline, main text area, status bar.

## Install

```bash
git clone https://github.com/<you>/dramaticpi.git
cd dramaticpi
./install.sh
```

Adds:

- `python3-pyqt5` and `python3-reportlab` via apt (skipped if already present)
- `~/.local/lib/dramaticpi` — the package
- `~/.local/bin/dramaticpi` — the launcher
- Menu entry under Office / Word Processor

## Use

Launch from the Applications menu, or run `dramaticpi`.

Scripts save with the `.dramapi` extension.

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

Exact numbers live in [`dramaticpi/layout.py`](dramaticpi/layout.py) — the single source of truth for the editor, PDF export, and HTML export.

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
