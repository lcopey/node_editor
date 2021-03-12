from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from node_editor.utils import dumpException
from utils import *

import sys
from typing import Union, List, Any, Iterable

DEBUG = False

class DraggableListItem(QListWidgetItem):
    def __init__(self, value):
        super(DraggableListItem, self).__init__()
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value: Union[Iterable, Any]):
        if type(new_value) != str and hasattr(new_value, '__iter__'):
            text = ', '.join(map(str, new_value))
        else:
            text = str(new_value)
        self._value = new_value
        self.setText(text)


class DraggableListWidget(QListWidget):
    itemDropped = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setDragDropMode(QListWidget.DragDrop)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAcceptDrops(True)

    def addItem(self, value: Any) -> None:
        item = DraggableListItem(value)
        super().addItem(item)

    def addItems(self, values: Iterable[Any]) -> None:
        for value in values:
            self.addItem(value)

    def startDrag(self, supportedActions: Union[Qt.DropActions, Qt.DropAction]) -> None:
        try:
            item: DraggableListItem = self.currentItem()
            drag = getDragObject(self, item)
            drag.exec_(Qt.MoveAction)
        except Exception as e:
            dumpException(e)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat(LISTBOX_W_VALUE_MIMETYPE):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.setAccepted(False)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(LISTBOX_W_VALUE_MIMETYPE):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.setAccepted(False)

    def dropEvent(self, event: QDropEvent) -> None:
        try:
            item = self.itemAt(event.pos())
            source = event.source()

            mime = event.mimeData()
            if mime.hasFormat(LISTBOX_W_VALUE_MIMETYPE):
                # Retrieve value from mime data
                value = getValueFromMime(mime)
                new_item = DraggableListItem(value)
                # find existing items with the same name and remove them
                # source is either self or the instance of DraggableListWidget
                source.removeItems(new_item.text())
                # Add new_item
                currentRow = self.row(item)
                self.insertItem(currentRow, new_item)
                self.itemDropped.emit()
                event.acceptProposedAction()
        except Exception as e:
            dumpException(e)

    def removeItems(self, text: str):
        existingItems = self.findItems(text, Qt.MatchExactly | Qt.MatchRecursive)
        for existingItem in existingItems:
            self.takeItem(self.row(existingItem))
