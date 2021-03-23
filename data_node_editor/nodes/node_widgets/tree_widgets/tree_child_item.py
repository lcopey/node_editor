from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtCore import Qt
from typing import Any


class ChildItem(QTreeWidgetItem):
    """Helper class instantiating a QTreeWidgetItem in a simple way"""

    def __init__(self, parent, value: Any, checked: Qt.CheckState = Qt.Checked):
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
        super().__init__(parent)
        self.value = value  # store the value untouched
        self.setText(0, str(value))  # set the text
        self.setFlags(self.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        self.setCheckState(0, checked)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
