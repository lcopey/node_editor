from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enum import Enum
from utils import *

from typing import TYPE_CHECKING, Optional, Union, List, Type


# implement
# - stack :
#   - level ? - dropdown
# - unstack
#   - ?
# - reset_index -> add additional arg axis
#   - axis - dropdown
# - melt :
#   - columns
# - pivot :
#   - columns
# - transpose
# - rename
#   - columns - qlineedit
# - sorting :
#   - columns
# - sort_index :
#   - axis - dropdown


class OptionTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, value):
        super(OptionTreeWidgetItem, self).__init__()
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if type(new_value) != str and hasattr(new_value, '__iter__'):
            text = ', '.join(map(str, new_value))
        else:
            text = str(new_value)
        self._value = new_value
        self.setText(0, text)


class OptionTreeWidget(QTreeWidget):
    itemClass = OptionTreeWidgetItem
    itemDropped = pyqtSignal()
    dropValidator = []

    def __init__(self, names: Union[List[str]], parent: Optional[QWidget] = None, acceptDrops: bool = False):
        super(OptionTreeWidget, self).__init__(parent=parent)
        if names:
            self.setHeaderLabels(names)
        self.setRootIsDecorated(True)
        self.setColumnCount(len(names))
        if acceptDrops:
            self.setDragDropMode(QListWidget.DragDrop)
            self.setSelectionMode(QListWidget.ExtendedSelection)
            self.setDefaultDropAction(Qt.MoveAction)
            self.setAcceptDrops(True)

    @classmethod
    def registerDropValidator(cls, callback: 'callable'):
        cls.dropValidator.append(callback)

    @classmethod
    def getDropValidator(cls):
        return cls.dropValidator

    def validateDrop(self, source, destination) -> bool:
        result = True
        for callback in self.dropValidator:
            result &= callback(self, source, destination)
        return result

    def addRootItem(self, itemName: str, widget: Optional[QWidget] = None, flags: Optional[Qt.ItemFlag] = None):
        root = self.invisibleRootItem()

        item = self.getItemClass()(itemName)
        if flags:
            item.setFlags(flags)
        root.addChild(item)

        if widget:
            widget.setParent(self)
            self.setItemWidget(item, 1, widget)

    def getItemClass(self) -> Type[OptionTreeWidgetItem]:
        return self.__class__.itemClass

    def startDrag(self, supportedActions: Union[Qt.DropActions, Qt.DropAction]) -> None:
        """Instantiate QDrag action when starting drag.

        Parameters
        ----------
        supportedActions: Union[Qt.DropActions, Qt.DropAction]

        Returns
        -------
        None
        """
        try:
            item: OptionTreeWidgetItem = self.currentItem()
            drag = getDragObject(self, item)
            drag.exec_(Qt.MoveAction)
        except Exception as e:
            dumpException(e)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Drag enter event.

        Accept `application/draggedItem` mime type.
        Parameters
        ----------
        event: QDragEnterEvent

        Returns
        -------
        None
        """
        if event.mimeData().hasFormat(LISTBOX_W_VALUE_MIMETYPE):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.setAccepted(False)

    def dragMoveEvent(self, event):
        """Drag move enter event.

        Accept `application/draggedItem` mime type.
        Parameters
        ----------
        event: QDragEnterEvent

        Returns
        -------
        None
        """
        if event.mimeData().hasFormat(LISTBOX_W_VALUE_MIMETYPE):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.setAccepted(False)

    def dropEvent(self, event: QDropEvent) -> None:
        """Drop enter event.

        Accept `application/draggedItem` mime type.
        Parameters
        ----------
        event: QDragEnterEvent

        Returns
        -------
        None
        """
        try:
            item = self.itemAt(event.pos())
            source = event.source()

            mime = event.mimeData()
            if mime.hasFormat(LISTBOX_W_VALUE_MIMETYPE):
                # Retrieve value from mime data
                value = getValueFromMime(mime)
                new_item = self.getItemClass()(value)
                # only add new item to DestTreeWidgetItem
                # it avoids having deep tree
                if self.validateDrop(source, item):
                    # find existing items with the same name and remove them
                    # source is either self or the instance of SourceListWidget
                    source.removeItems(new_item.text(0))

                    # Add new_item
                    item.addChild(new_item)
                    event.acceptProposedAction()
                    self.itemDropped.emit()

        except Exception as e:
            dumpException(e)

    def removeItems(self, text):
        existingItems = self.findItems(text, Qt.MatchExactly | Qt.MatchRecursive)
        for existingItem in existingItems:
            (existingItem.parent() or self.invisibleRootItem()).removeChild(existingItem)
