from PyQt5.QtWidgets import QTreeView, QTreeWidget, QTreeWidgetItem
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QModelIndex, Qt
from dataclasses import dataclass
import pandas as pd
import numpy as np

from typing import Union, Any


class DictLike:
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


# @dataclass
# class Item:
#     state: bool
#     text: str
#     parent:


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
        checked: bool
            current value of the checkbox
        """
        super().__init__(parent)
        self.type = type(value)
        self.setText(0, str(value))
        self.setFlags(self.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        self.setCheckState(0, checked)


class HierarchicalTreeWidget(QTreeWidget):
    """Widget implementing a tree view of dataframe header"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setHeaderHidden(True)
        # self.setColumnCount(2)  # in case additional information are needed

    def init_model(self, values: Union[pd.Index, pd.MultiIndex]):
        self.clear()
        level_values = np.array([np.array(value) for value in values])
        self._recursive_add(self, level_values)

    def _recursive_add(self, parent, level_values):
        """Recursively add inner items to the treeWidget

        Parameters
        ----------
        parent: Union[QTreeWidgetItem, QTreeWidget]
            parent item to add the inner values to
        level_values: np.array
            array containing level values (nlevel, values)
        """
        # If not the last level
        if level_values.ndim > 1 and level_values.shape[1] > 1:
            outer_levels = level_values[:, 0]
            unique_levels = np.unique(outer_levels)
            for level in unique_levels:
                inner_item = ChildItem(parent, level)
                inner_levels = level_values[outer_levels == level, 1:]
                self._recursive_add(inner_item, inner_levels)

        # last level, simply add the items
        else:
            unique_levels = np.unique(level_values)
            for level in unique_levels:
                inner_item = ChildItem(parent, level)
