#!/usr/bin/env bash
# Installs DramaticPi for the current user on Raspberry Pi OS (Bullseye+).
# - apt-installs python3-pyqt5 and python3-reportlab (skip if present)
# - copies the dramaticpi package to ~/.local/lib/dramaticpi
# - drops a launcher into ~/.local/bin/dramaticpi
# - drops a .desktop file into ~/.local/share/applications

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PREFIX="${HOME}/.local"
LIB_DIR="${PREFIX}/lib/dramaticpi"
BIN="${PREFIX}/bin/dramaticpi"
DESKTOP="${PREFIX}/share/applications/dramaticpi.desktop"

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
rm -rf "${LIB_DIR}/dramaticpi"
cp -r "${REPO_DIR}/dramaticpi" "${LIB_DIR}/dramaticpi"

echo "==> Installing launcher: ${BIN}"
mkdir -p "$(dirname "${BIN}")"
cat > "${BIN}" <<EOF
#!/usr/bin/env bash
export PYTHONPATH="${LIB_DIR}:\${PYTHONPATH:-}"
exec python3 -m dramaticpi "\$@"
EOF
chmod +x "${BIN}"

echo "==> Installing desktop entry: ${DESKTOP}"
mkdir -p "$(dirname "${DESKTOP}")"
cp "${REPO_DIR}/dramaticpi.desktop" "${DESKTOP}"
sed -i "s|@BIN@|${BIN}|g" "${DESKTOP}"

echo "==> Done. Launch from your applications menu or run: dramaticpi"
