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
