import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt
from .tree_child_item import ChildItem
from typing import Union, List, Tuple, TYPE_CHECKING


class CheckableHierarchicalTreeWidget(QTreeWidget):
    """Widget implementing a hierarchical tree view of dataframe header"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setHeaderHidden(True)
        # self.itemClicked.connect(self.debug)
        # self.setColumnCount(2)  # in case additional information are needed

    def initModel(self, values: Union[pd.Index, pd.MultiIndex, np.array], include_checked: bool = False) -> None:
        """Initialize inner model from array-like values.

        Examples of values includes pd.Index, pd.MultiIndex and np.array.
        Parameters
        ----------
        values: Union[pd.Index, pd.MultiIndex, np.array]
            instance of an Index or Multindex of a dataframe
        include_checked: bool
            if ``True``, values should include boolean values in the last columns stating which ones are checked or not

        Returns
        -------
        None
        """

        def recurse(parent: Union[QTreeWidgetItem, QTreeWidget], level_values: np.array, checked: np.array):
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
                    recurse(inner_item, inner_levels, checked[outer_levels == level])

            # last level, simply add the items
            else:
                unique_levels = np.unique(level_values)
                for level, check in zip(unique_levels, checked):
                    inner_item = ChildItem(parent, level, Qt.Checked if check else Qt.Unchecked)

        self.clear()
        # set the type as O to keep the data type intact
        if isinstance(values, pd.MultiIndex):
            level_values = np.array([list(value) for value in values], dtype='O')
        else:
            level_values = np.array(values, dtype='O')

        if include_checked:
            # last columns contains checked values
            checked = level_values[:, -1]
            level_values = level_values[:, :-1]
        else:
            checked = np.ones(level_values.shape[0], dtype=bool)

        recurse(self, level_values, checked)

    def getItems(self, selected_only=True) -> List[Tuple]:
        """Recursively walk the tree and returns checked items as a list of tuple

        Returns
        -------
        List[Tuple]
            List of tuple values

        """
        checked_items = []

        def recurse(parent_item: Union[QTreeWidgetItem, QTreeWidget], inner_level: Union[List, None]):
            # inner level
            leaves_count = parent_item.childCount()
            # walk on each children
            for i in range(leaves_count):
                child = parent_item.child(i)
                if child.childCount() > 0:
                    # inner level
                    value = child.value
                    if inner_level is None:
                        inner_level = [value]
                    else:
                        inner_level.append(value)
                    recurse(child, inner_level)

                else:
                    # Last level
                    if selected_only:
                        if child.checkState(0) == Qt.Checked:
                            value = child.value
                            # append level values to checked items
                            if inner_level is None:
                                checked_items.append(value)
                            else:
                                checked_items.append((*inner_level, value))
                    else:
                        value = child.value
                        checked = child.checkState(0) == Qt.Checked
                        # append level values to checked items
                        if inner_level is None:
                            checked_items.append((value, checked))
                        else:
                            checked_items.append((*inner_level, value, checked))

                if i == leaves_count - 1 and inner_level and len(inner_level) > 0:
                    inner_level.pop(-1)

        root = self.invisibleRootItem()
        recurse(root, None)

        return checked_items

    def checkAll(self):
        root = self.invisibleRootItem()
        for n in range(root.childCount()):
            child = root.child(n)
            child.setCheckState(0, Qt.Checked)

    def checkNone(self):
        root = self.invisibleRootItem()
        for n in range(root.childCount()):
            child = root.child(n)
            child.setCheckState(0, Qt.Unchecked)

    def debug(self):
        print(self.getItems())
