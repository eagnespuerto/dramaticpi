#!/usr/bin/env bash
set -euo pipefail

PREFIX="${HOME}/.local"
rm -rf "${PREFIX}/lib/piscript"
rm -f  "${PREFIX}/bin/piscript"
rm -f  "${PREFIX}/share/applications/piscript.desktop"
echo "piscript uninstalled. apt packages (python3-pyqt5, python3-reportlab) were left in place."
