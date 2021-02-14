from PyQt5.QtWidgets import QTreeView, QTreeWidget, QTreeWidgetItem
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QModelIndex, Qt
import pandas as pd
import numpy as np

from typing import Union, Any


class ChildItem(QTreeWidgetItem):
    def __init__(self, parent, text: str, checked: Qt.CheckState = Qt.Checked):
        super().__init__(parent)
        self.setText(0, text)
        self.setFlags(self.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        self.setCheckState(0, checked)


class HeaderTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setHeaderHidden(True)

    def init_model(self, header_values: Union[pd.Index, pd.MultiIndex]):
        level_values = np.array([np.array(value) for value in header_values])
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
        if level_values.ndim > 1 and level_values.shape[1] > 1:
            outer_levels = level_values[:, 0]
            unique_levels = np.unique(outer_levels)
            for level in unique_levels:
                inner_item = ChildItem(parent, level)
                inner_levels = level_values[outer_levels == level, 1:]
                self._recursive_add(inner_item, inner_levels)
        else:
            unique_levels = np.unique(level_values)
            for level in unique_levels:
                inner_item = ChildItem(parent, level)
