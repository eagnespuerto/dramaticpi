#!/usr/bin/env bash
set -euo pipefail

PREFIX="${HOME}/.local"
rm -rf "${PREFIX}/lib/dramaticpi"
rm -f  "${PREFIX}/bin/dramaticpi"
rm -f  "${PREFIX}/share/applications/dramaticpi.desktop"
echo "DramaticPi uninstalled. apt packages (python3-pyqt5, python3-reportlab) were left in place."
