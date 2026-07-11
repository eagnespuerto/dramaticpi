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
