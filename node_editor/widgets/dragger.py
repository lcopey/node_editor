from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from node_editor.utils import dumpException

import sys
from typing import Union, List, Any


def getData(itemData: QByteArray, value: Any):
    """Construct a QDataStream containing item value as a QVariantList

    Parameters
    ----------
    itemData: QByteArray
    """
    dataStream = QDataStream(itemData, QIODevice.WriteOnly)
    if not hasattr(value, '__iter__'):
        dataStream.writeQVariantList([value])
    else:
        dataStream.writeQVariantList(value)


def getDragObject(parent: QWidget, item: Union['SourceListWidgetItem', 'DestTreeWidgetItem']) -> QDrag:
    """Instantiate QDrag of type application/draggerItem with corresponding QMimeData

    Parameters
    ----------
    parent: QWidget
    item: Union['SourceListWidgetItem', 'DestTreeWidgetItem']

    Returns
    -------
    QDrag
        QDrag object holding item value as QMimeData
    """
    # construct dataStream with item value
    itemData = QByteArray()
    getData(itemData, item.value)

    mimeData = QMimeData()
    mimeData.setData('application/draggerItem', itemData)

    drag = QDrag(parent)
    drag.setHotSpot(QPoint(0, 0))
    drag.setMimeData(mimeData)
    return drag


def getValueFromMime(mime):
    itemData = mime.data('application/draggerItem')
    dataStream = QDataStream(itemData, QIODevice.ReadOnly)
    value = dataStream.readQVariantList()
    if len(value) == 1:
        value = value[0]
    else:
        value = tuple(value)
    return value


class SourceListWidgetItem(QListWidgetItem):
    def __init__(self, value):
        super(SourceListWidgetItem, self).__init__()
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if hasattr(new_value, '__iter__'):
            text = ', '.join(map(str, new_value))
        else:
            text = str(new_value)
        self._value = new_value
        self.setText(text)


class SourceListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragDropMode(QListWidget.DragDrop)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAcceptDrops(True)

    def startDrag(self, supportedActions: Union[Qt.DropActions, Qt.DropAction]) -> None:
        try:
            item: SourceListWidgetItem = self.currentItem()
            drag = getDragObject(self, item)
            drag.exec_(Qt.MoveAction)
        except Exception as e:
            dumpException(e)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat('application/draggerItem'):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.setAccepted(False)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/draggerItem'):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.setAccepted(False)

    def dropEvent(self, event: QDropEvent) -> None:
        try:
            item = self.itemAt(event.pos())
            source = event.source()

            mime = event.mimeData()
            if mime.hasFormat('application/draggerItem'):
                # Retrieve value from mime data
                value = getValueFromMime(mime)
                new_item = SourceListWidgetItem(value)
                # find existing items with the same name and remove them
                # source is either self or the instance of SourceListWidget
                source.removeItems(new_item.text())
                # Add new_item
                currentRow = self.row(item)
                self.insertItem(currentRow, new_item)
                event.acceptProposedAction()
        except Exception as e:
            dumpException(e)

    def removeItems(self, text: str):
        existingItems = self.findItems(text, Qt.MatchExactly | Qt.MatchRecursive)
        for existingItem in existingItems:
            self.takeItem(self.row(existingItem))


class DestTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, value):
        super(DestTreeWidgetItem, self).__init__()
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if hasattr(new_value, '__iter__'):
            text = ', '.join(map(str, new_value))
        else:
            text = str(new_value)
        self._value = new_value
        self.setText(0, text)


class DestTreeWidget(QTreeWidget):
    itemDropped = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.header().hide()
        self.setRootIsDecorated(False)
        self.setDragDropMode(QListWidget.DragDrop)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAcceptDrops(True)

    def startDrag(self, supportedActions: Union[Qt.DropActions, Qt.DropAction]) -> None:
        try:
            item: SourceListWidgetItem = self.currentItem()
            drag = getDragObject(self, item)
            drag.exec_(Qt.MoveAction)
        except Exception as e:
            dumpException(e)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat('application/draggerItem'):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.setAccepted(False)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/draggerItem'):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.setAccepted(False)

    def dropEvent(self, event: QDropEvent) -> None:
        try:
            item = self.itemAt(event.pos())
            source = event.source()

            mime = event.mimeData()
            if mime.hasFormat('application/draggerItem'):
                # Retrieve value from mime data
                value = getValueFromMime(mime)
                new_item = DestTreeWidgetItem(value)
                # only add new item to DestTreeWidgetItem
                # it avoids having deep tree
                if not isinstance(item, DestTreeWidgetItem):
                    # find existing items with the same name and remove them
                    # source is either self or the instance of SourceListWidget
                    source.removeItems(new_item.text(0))

                    # Add new_item
                    item.addChild(new_item)
                    event.acceptProposedAction()

        except Exception as e:
            dumpException(e)

    def removeItems(self, text):
        existingItems = self.findItems(text, Qt.MatchExactly | Qt.MatchRecursive)
        for existingItem in existingItems:
            (existingItem.parent() or self.invisibleRootItem()).removeChild(existingItem)


class Dragger(QWidget):
    def __init__(self, fromListLabel: str = 'Input', toListNames: Union[List[str], None] = None):
        super().__init__()
        self.sourceList: Union[QListWidget, None] = None
        self.search_bar: Union[QLineEdit, None] = None
        self.listLbl: Union[QLabel, None] = None
        self.toTree: Union[QTreeWidget, None] = None
        self.initUI(fromListLabel, toListNames)

    def initUI(self, fromListLabel: str, toListNames: Union[List[str], None]):
        if toListNames is None:
            toListNames = ['output']

        self.sourceList = SourceListWidget()
        self.search_bar = QLineEdit()
        self.listLbl = QLabel(fromListLabel)

        # Define destination tree
        self.toTree = DestTreeWidget()

        root = self.toTree.invisibleRootItem()
        root.setFlags(Qt.NoItemFlags)

        for name in toListNames:
            item = QTreeWidgetItem(root)
            item.setText(0, name)
            item.setExpanded(True)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled)

        layout = QVBoxLayout()
        layout.addWidget(self.search_bar)
        layout.addWidget(self.listLbl)
        layout.addWidget(self.sourceList)
        layout.addWidget(self.toTree)
        self.setLayout(layout)

    def initModel(self, values: List[Any]):
        for value in values:
            item = SourceListWidgetItem(value)
            self.sourceList.addItem(item)

    def debug(self):
        print('dropped')
        try:
            settings = dict()
            root = self.toTree.invisibleRootItem()
            for n in range(root.childCount()):
                child = root.child(n)
                settings[child.text(0)] = list()
                if child.childCount() > 0:
                    for i in range(child.childCount()):
                        print(child.child(i).value)
        except Exception as e:
            dumpException(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dragger = Dragger(toListNames=['output_1', 'output_2'])
    dragger.initModel([(n, 'input{}'.format(n)) for n in range(10)])
    dragger.show()
    sys.exit(app.exec_())
