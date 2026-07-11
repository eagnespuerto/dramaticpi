"""ScriptEdit — a QTextEdit that renders script layouts and cycles element types."""

from __future__ import annotations

from PyQt5.QtCore import QSizeF, Qt, pyqtSignal
from PyQt5.QtGui import (
    QFont, QKeyEvent, QTextBlockFormat, QTextCharFormat, QTextCursor,
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

        self._apply_page_size()
        self.cursorPositionChanged.connect(self._emit_current_element)
        self.textChanged.connect(self._maybe_emit_page_count)

    def mode(self) -> Mode:
        return self._mode

    def set_mode(self, mode: Mode) -> None:
        self._mode = mode
        self._apply_page_size()
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
            state = b.userState()
            t = _decode_state(state) if state >= _USER_STATE_BASE else ElementType.ACTION
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
        return max(1, self.document().pageCount())

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

        if mods & Qt.ControlModifier and Qt.Key_1 <= key <= Qt.Key_9:
            idx = key - Qt.Key_1
            elements = valid_elements(self._mode)
            if idx < len(elements):
                self.set_element_at_cursor(elements[idx])
                event.accept()
                return

        super().keyPressEvent(event)
        self._maybe_apply_heuristics()

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
        usable_w = (metrics.width_inch - metrics.left_inch - metrics.right_inch) * POINTS_PER_INCH
        self.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.setLineWrapColumnOrWidth(int(usable_w))

    def _apply_block_format(self, cursor: QTextCursor, element: ElementType) -> None:
        style: ElementStyle = style_for(self._mode, element)

        block_fmt = QTextBlockFormat()
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

        c = QTextCursor(cursor.block())
        c.select(QTextCursor.BlockUnderCursor)
        c.setBlockFormat(block_fmt)
        c.setCharFormat(char_fmt)

    def _emit_current_element(self) -> None:
        self.element_changed.emit(self.element_at_cursor())
        self._maybe_emit_page_count()

    def _maybe_emit_page_count(self) -> None:
        total = self.page_count()
        self.page_changed.emit(1, total)
