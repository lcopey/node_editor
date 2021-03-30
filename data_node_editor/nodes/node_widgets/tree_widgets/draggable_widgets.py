from PyQt5.QtWidgets import QWidget, QListWidget, QTreeWidget, QApplication, QMainWindow, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt
from node_editor.utils import dumpException
from typing import Union
from .child_items import ValuedItem, ListItem, TreeItem
from .utils import LISTBOX_W_VALUE_MIMETYPE


class Draggable(QWidget):
    """Is intented to be subclassed by QTreeWidget or QListWidget"""
    itemDropped = None
    itemClass = ValuedItem

    def __init__(self, parent=None):
        super(Draggable, self).__init__(parent)
        self.initDragOptions()
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAcceptDrops(True)

    def initDragOptions(self):
        if isinstance(self, QListWidget):
            self.setDragDropMode(QListWidget.DragDrop)
            self.setSelectionMode(QListWidget.ExtendedSelection)
        elif isinstance(self, QTreeWidget):
            self.setDragDropMode(QTreeWidget.DragDrop)
            self.setSelectionMode(QTreeWidget.ExtendedSelection)

    def getItemClass(self):
        return self.__class__.itemClass

    def startDrag(self, supportedActions: Union[Qt.DropActions, Qt.DropAction]) -> None:
        try:
            item: ValuedItem = self.currentItem()
            drag = item.getDrag(self)
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
                new_item = self.getItemClass().from_mime(mime)
                self.finishDrop(item, source, new_item)
                assert self.itemDropped is not None, 'itemDropped should be reimplemented'
                self.itemDropped.emit()
                event.acceptProposedAction()
        except Exception as e:
            dumpException(e)

    def finishDrop(self, item_at, source, new_item):
        raise NotImplementedError

    def removeItems(self, text: str):
        raise NotImplementedError


class DraggableListWidget(QListWidget, Draggable):
    itemClass = ListItem
    itemDropped = pyqtSignal()

    def __init__(self, parent=None):
        super(DraggableListWidget, self).__init__(parent)

    def finishDrop(self, item_at, source, new_item):
        source.removeItems(new_item.text())
        currentRow = self.row(item_at)
        self.insertItem(currentRow, new_item)

    def removeItems(self, text: str):
        existingItems = self.findItems(text, Qt.MatchExactly | Qt.MatchRecursive)
        for existingItem in existingItems:
            self.takeItem(self.row(existingItem))


class DraggableTreeWidget(QTreeWidget, Draggable):
    itemClass = TreeItem
    itemDropped = pyqtSignal()

    def __init__(self, parent=None):
        super(DraggableTreeWidget, self).__init__(parent)

    def finishDrop(self, item_at, source, new_item):
        source.removeItems(new_item.text(0))
        if item_at is None:
            item_at = self.invisibleRootItem()
        item_at.addChild(new_item)

    def removeItems(self, text: str):
        existingItems = self.findItems(text, Qt.MatchExactly | Qt.MatchRecursive)
        for existingItem in existingItems:
            (existingItem.parent() or self.invisibleRootItem()).removeChild(existingItem)
