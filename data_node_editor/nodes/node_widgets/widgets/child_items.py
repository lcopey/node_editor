from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDrag
from typing import Union, Iterable, Any
from .utils import _getDragObject, _getValueFromMime


class ValuedItem:
    """Base class holding value.

    It is intented to hold a value identifying a column or an index from a pd.DataFram
    To be subclassed with QAbstractModelItem from Qt"""

    def __init__(self, value: Any):
        self.value = value

    @classmethod
    def from_mime(cls, mime):
        value = _getValueFromMime(mime)
        return cls(value=value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value: Union[Iterable, Any]):
        # in case of iterable value, join with ', '
        if new_value is None:
            text = ''
        elif type(new_value) != str and hasattr(new_value, '__iter__'):
            text = ', '.join(map(str, new_value))
        # else simply cast to str
        else:
            text = str(new_value)
        self._value = new_value
        self.setLabel(text)

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

    def setLabel(self, text: str):
        raise NotImplementedError


class ListItem(QListWidgetItem, ValuedItem):
    """Helper class instantiating a ListWidgetItem holding value of any type. It is intended to be used in a
    draggable ListWidget."""

    def __init__(self, parent=None, value: Any = None):
        """Helper class holding value

        Value can be of any type. It is stored as it is but displayed as str
        Parameters
        ----------
        value: Any
            value to store in the item. This is typically the value of a specific header or index to store.
        """
        super(ListItem, self).__init__(parent, value=value)

    def setLabel(self, text):
        self.setText(text)


class TreeItem(QTreeWidgetItem, ValuedItem):
    """Helper class instantiating a QTreeWidgetItem in a simple way"""

    def __init__(self, parent=None, value: Any = None,
                 checkable: bool = False, checked: Qt.CheckState = Qt.Checked):
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
        super(TreeItem, self).__init__(parent, value=value)
        flags = self.flags()
        if checkable:
            flags = flags | Qt.ItemIsTristate | Qt.ItemIsUserCheckable
        self.setFlags(flags)
        if checkable:
            self.setCheckState(0, checked)

    def setLabel(self, text):
        self.setText(0, text)
