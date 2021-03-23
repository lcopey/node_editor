from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from node_editor.utils import dumpException
import pandas as pd

import sys
from typing import Union, List, Any, Iterable

LISTBOX_W_VALUE_MIMETYPE = "application/draggedItem"

DEBUG = False


def getData(itemData: QByteArray, value: Any):
    """Construct a QDataStream containing item value as a QVariantList

    Parameters
    ----------
    itemData: QByteArray
    """
    dataStream = QDataStream(itemData, QIODevice.WriteOnly)
    if (type(value) == str) or not hasattr(value, '__iter__'):
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
    mimeData.setData(LISTBOX_W_VALUE_MIMETYPE, itemData)

    drag = QDrag(parent)
    drag.setHotSpot(QPoint(0, 0))
    drag.setMimeData(mimeData)
    return drag


def getValueFromMime(mime):
    itemData = mime.data(LISTBOX_W_VALUE_MIMETYPE)
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
    def value(self, new_value: Union[Iterable, Any]):
        if type(new_value) != str and hasattr(new_value, '__iter__'):
            text = ', '.join(map(str, new_value))
        else:
            text = str(new_value)
        self._value = new_value
        self.setText(text)


class SourceListWidget(QListWidget):
    itemDropped = pyqtSignal()

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
                new_item = SourceListWidgetItem(value)
                # find existing items with the same name and remove them
                # source is either self or the instance of SourceListWidget
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


class DestTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, value):
        super(DestTreeWidgetItem, self).__init__()
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


class DestTreeWidget(QTreeWidget):
    itemDropped = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.header().hide()
        self.setRootIsDecorated(True)
        self.setItemsExpandable(False)
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
                    self.itemDropped.emit()

        except Exception as e:
            dumpException(e)

    def removeItems(self, text):
        existingItems = self.findItems(text, Qt.MatchExactly | Qt.MatchRecursive)
        for existingItem in existingItems:
            (existingItem.parent() or self.invisibleRootItem()).removeChild(existingItem)


class Dragger(QWidget):
    """Widget holding a QListWidget of items draggable to a QTreeWidget.

    Signals
    -------
    itemDropped : Event triggered when a item is dropped either in the input list or the output tree"""
    itemDropped = pyqtSignal()

    def __init__(self, inputTitle: str = 'Input', outputNames: Union[List[str], None] = None):
        """Instantiate a widget holding a QListWidget of items draggable to a QTreeWidget

        Parameters
        ----------
        inputTitle: str
            Title over the list inputs
        outputNames : List[str]
            Name of each leaf of the output tree
        """
        super().__init__()
        self.inputList: Union[QListWidget, None] = None
        self.search_bar: Union[QLineEdit, None] = None
        self.inputListLabel: Union[QLabel, None] = None
        self.outputTree: Union[QTreeWidget, None] = None
        self.inputLabel = inputTitle
        self.outputNames = outputNames
        self.initUI()

    def initUI(self):
        if self.outputNames is None:
            self.outputNames = ['output']
        # instantiate input widgets
        self.inputListLabel = QLabel(self.inputLabel)
        self.search_bar = QLineEdit()
        self.search_bar.textChanged.connect(self.filter)
        self.search_bar.textChanged.connect(self.filter)
        self.search_bar.setPlaceholderText('Filter')
        self.inputList = SourceListWidget()
        self.inputList.itemDropped.connect(self.onItemDropped)

        # Define destination tree
        self.outputTree = DestTreeWidget()
        self.outputTree.itemDropped.connect(self.onItemDropped)

        root = self.outputTree.invisibleRootItem()
        root.setFlags(Qt.NoItemFlags)

        # add outputNames as leaf
        for name in self.outputNames:
            item = QTreeWidgetItem(root)
            item.setText(0, name)
            item.setExpanded(True)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled)

        # layout holding inputs widgets
        upperLayout = QVBoxLayout()
        upperLayout.addWidget(self.inputListLabel)
        upperLayout.addWidget(self.search_bar)
        upperLayout.addWidget(self.inputList)
        # layout holding the tree widget
        bottomLayout = QVBoxLayout()
        bottomLayout.addWidget(self.outputTree)

        # add widgets to frames
        upperFrame = QFrame()
        upperFrame.setFrameShape(QFrame.StyledPanel)
        upperFrame.setLayout(upperLayout)
        bottomFrame = QFrame()
        bottomFrame.setFrameShape(QFrame.StyledPanel)
        bottomFrame.setLayout(bottomLayout)

        # final layout is composed of both frame
        outerLayout = QVBoxLayout()
        outerLayout.addWidget(upperFrame)
        outerLayout.addWidget(bottomFrame)
        self.setLayout(outerLayout)

    def initModel(self, values: Union[Iterable[Any], pd.Index, pd.MultiIndex, None]):
        """Initiate the widget with the values.

        Initiate the input QListWidget with the values.
        All child items of the output tree are also removed except for those directly connected to the root.
        Parameters
        ----------
        values: Union[Iterable[Any], pd.Index, pd.MultiIndex, None]
            Iterable of any values, each value are represented as a string in the widget. The inital value is retained
            as an attribute of each item. Each value are supposed to be unique

        Returns
        -------
        None
        """
        # Get current set of values
        currentStatus = self.getStatus()
        currentValues = set(currentStatus['inputs'])
        for key, value in currentStatus['outputs'].items():
            currentValues = currentValues.union(set(value))

        # in case both set are identical, do not update
        if set(values) != currentValues:
            self.print('initModel')
            self.print(values, currentValues)
            # init source list with values
            self.inputList.clear()
            if values is not None:
                for value in values:
                    item = SourceListWidgetItem(value)
                    self.inputList.addItem(item)

            # clear outputTree
            root = self.outputTree.invisibleRootItem()
            for n in range(root.childCount()):
                child = root.child(n)
                if child.childCount() > 0:
                    for i in range(child.childCount()):
                        child.removeChild(child.child(i))

    def onItemDropped(self):
        """Event triggered when a item is dropped either in the input list or the output tree"""
        self.itemDropped.emit()

    def filter(self):
        """Filter the input list based on the search bar text."""
        # Hide every items of the input list
        for i in range(self.inputList.count()):
            self.inputList.item(i).setHidden(True)

        # find items corresponding to the search bar text
        # and hide them
        items = self.inputList.findItems(f".*{self.search_bar.text()}.*", Qt.MatchRegExp | Qt.MatchRecursive)
        for item in items:
            item.setHidden(False)

    def getStatus(self) -> dict:
        """Returns a dictionary holding the values of the widgets

        Returns a dictionary of the form :
        - 'inputList': List of values in the inputList,
        - 'outputTree' :
            - outputName1 : List of values
            - outputName2 : List of values
            - ...
        Returns
        -------
        dict

        """
        status = {'inputs': list()}
        for i in range(self.inputList.count()):
            status['inputs'].append(self.inputList.item(i).value)

        status['outputs'] = dict()
        root = self.outputTree.invisibleRootItem()
        for i in range(root.childCount()):
            child = root.child(i)
            key = child.text(0)
            status['outputs'][key] = list()
            if child.childCount() > 0:
                for j in range(child.childCount()):
                    status['outputs'][key].append(child.child(j).value)

        return status

    def restoreStatus(self, data: dict) -> bool:
        """Restore the status of the widget.

        Restore the status of the widget using a dictionary with keys 'input', 'output' as returned by getStatus method.
        Parameters
        ----------
        data: dict
            dictionary as returned by the method getStatus

        Returns
        -------
        ``bool``
            True if successful
        """
        try:
            # restore inputs
            self.inputList.clear()
            if data['inputs'] is not None:
                for value in data['inputs']:
                    item = SourceListWidgetItem(value)
                    self.inputList.addItem(item)

            # restore outputs
            root = self.outputTree.invisibleRootItem()
            for n in range(root.childCount()):
                child = root.child(n)
                # remove current child items in case of any
                if child.childCount() > 0:
                    for i in range(child.childCount()):
                        child.removeChild(child.child(i))
                # add child items to the corresponding leaf
                key = child.text(0)
                for value in data['outputs'][key]:
                    item = DestTreeWidgetItem(value)
                    child.addChild(item)
            return True
        except Exception as e:
            dumpException(e)

        return False

    def debug(self):
        print('dropped')
        try:
            settings = dict()
            root = self.outputTree.invisibleRootItem()
            for n in range(root.childCount()):
                child = root.child(n)
                settings[child.text(0)] = list()
                if child.childCount() > 0:
                    for i in range(child.childCount()):
                        print(child.child(i).value)
        except Exception as e:
            dumpException(e)

    def print(self, *args):
        if DEBUG:
            print('Dragger>', *args)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dragger = Dragger(outputNames=['output_1', 'output_2'])
    dragger.initModel([(n, 'input{}'.format(n)) for n in range(10)])
    dragger.show()
    sys.exit(app.exec_())
