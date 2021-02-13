from PyQt5.QtWidgets import QTreeView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QModelIndex
import pandas as pd
import numpy as np

from typing import Union, Any


class HeaderTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def initModel(self, header_values: Union[pd.Index, pd.MultiIndex]):
        levels = np.array([np.array(value) for value in header_values])
        treeModel = QStandardItemModel()
        rootItem = treeModel.invisibleRootItem()
        self._recursive_add(levels, rootItem)
        self.setModel(treeModel)

    def _recursive_add(self, levels: np.array, item: QStandardItem, mapping: Union[dict, list]):
        if levels.shape[1] > 1:
            outer_level = levels[:, 0]
            unique_levels = np.unique(outer_level)
            for level in unique_levels:
                inner_levels = levels[outer_level == level, 1:]
                lower_item = QStandardItem()
                if inner_levels.shape[1] > 1:
                    mapping[level] = dict()
                else:
                    mapping[level] = list()
                item.appendRow(lower_item)
                self._recursive_add(inner_levels, lower_item)
        else:
            unique_levels = np.unique(levels)
            item.appendRows(unique_levels)
            mapping.extend(unique_levels)
