from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QListWidgetItem
from PyQt5.QtCore import Qt, QByteArray, QMimeData, QPoint, QDataStream, QIODevice
from PyQt5.QtGui import QDrag
from typing import Union, Iterable, Any

LISTBOX_W_VALUE_MIMETYPE = "application/draggedItem"


def _getData(itemData: QByteArray, value: Any):
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


# TODO include in child item class
def _getDragObject(parent: QWidget, item: Union['ListItem', 'TreeItem']) -> QDrag:
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
    _getData(itemData, item.value)

    mimeData = QMimeData()
    mimeData.setData(LISTBOX_W_VALUE_MIMETYPE, itemData)

    drag = QDrag(parent)
    drag.setHotSpot(QPoint(0, 0))
    drag.setMimeData(mimeData)
    return drag


class ListItem(QListWidgetItem):
    """Helper class instantiating a ListWidgetItem holding value of any type. It is intended to be used in a
    draggable ListWidget."""

    def __init__(self, value: Any):
        """Helper class holding value

        Value can be of any type. It is stored as it is but displayed as str
        Parameters
        ----------
        value: Any
            value to store in the item. This is typically the value of a specific header or index to store.
        """
        super(ListItem, self).__init__()
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value: Union[Iterable, Any]):
        # in case of iterable value, join with ', '
        if type(new_value) != str and hasattr(new_value, '__iter__'):
            text = ', '.join(map(str, new_value))

        # else simply cast to str
        else:
            text = str(new_value)

        self._value = new_value
        self.setText(text)

    def getDrag(self, parent: QWidget) -> QDrag:
        """Instantiate QDrag of type application/draggerItem with corresponding QMimeData

        Parameters
        ----------
        parent: QWidget

        Returns
        -------
        QDrag
            QDrag object holding item value as QMimeData
        """
        return _getDragObject(parent, self)


class TreeItem(QTreeWidgetItem):
    """Helper class instantiating a QTreeWidgetItem in a simple way"""

    def __init__(self, parent, value: Any, checkable: bool = True, checked: Qt.CheckState = Qt.Checked):
        """Helper class instantiating a QTreeWidget

        Parameters
        ----------
        parent: Union[QTreeWidget, QTreeWidgetItem]
            parent of the current item
        value: Any
            text to set the current item to
        checked: Qt.CheckState
            current value of the checkbox
        """
        super(TreeItem, self).__init__(parent)
        self.value = value  # store the value and set text
        flags = self.flags()
        if checkable:
            flags = flags | Qt.ItemIsTristate | Qt.ItemIsUserCheckable
        self.setFlags(flags)
        if checkable:
            self.setCheckState(0, checked)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value: Union[Iterable, Any]):
        # in case of iterable value, join with ', '
        if type(new_value) != str and hasattr(new_value, '__iter__'):
            text = ', '.join(map(str, new_value))

        # else simply cast to str
        else:
            text = str(new_value)

        self._value = new_value
        self.setText(text)

    def getDrag(self, parent: QWidget):
        """Instantiate QDrag of type application/draggerItem with corresponding QMimeData

        Parameters
        ----------
        parent: QWidget

        Returns
        -------
        QDrag
            QDrag object holding item value as QMimeData
        """
        return _getDragObject(parent, self)
