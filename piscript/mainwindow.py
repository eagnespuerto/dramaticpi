"""The main window: menu bar, toolbar, outline dock, editor, status bar."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAction, QComboBox, QDockWidget, QLabel, QMainWindow, QMessageBox,
    QToolBar,
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

        self._doc = Document()
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

    def _open(self):
        if not self._confirm_discard():
            return
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Open .piscript", "", "piscript files (*.piscript);;All files (*)"
        )
        if not path:
            return
        from . import model as _model
        try:
            result = _model.load(path)
        except _model.UnsupportedVersionError as e:
            QMessageBox.warning(
                self, "piscript",
                f"{e}\n\nThe file will be opened read-only as plain text."
            )
            return
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

    def _about(self):
        QMessageBox.about(
            self, "About piscript",
            "piscript — lightweight scriptwriting for stage and screen.\n"
            "MIT licensed. Made for Raspberry Pi.",
        )

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
        from PyQt5.QtGui import QTextCursor
        doc = self._editor.document()
        b = doc.findBlockByNumber(block_index)
        if b.isValid():
            cur = QTextCursor(b)
            self._editor.setTextCursor(cur)
            self._editor.setFocus()
