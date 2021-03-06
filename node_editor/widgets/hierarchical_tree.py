from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from node_editor.utils import dumpException
from dataclasses import dataclass
import pandas as pd
import numpy as np
import sys

from typing import Union, Any, List, Tuple


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


class TreeWidgetUI(QWidget):
    itemChecked = pyqtSignal()

    def __init__(self, parent=None):
        super(TreeWidgetUI, self).__init__()
        self.treeWidget = HierarchicalTreeWidget(parent)

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        select_all = QPushButton()
        select_all.setIcon(QIcon(QPixmap('icons/check-all-button.svg')))
        select_all.setIconSize(QSize(16, 16))
        select_all.clicked.connect(self.checkAll)

        select_none = QPushButton()
        select_none.setIcon(QIcon(QPixmap('icons/check-none-button.svg')))
        select_none.setIconSize(QSize(16, 16))
        select_none.clicked.connect(self.checkNone)

        expand_all = QPushButton()
        expand_all.clicked.connect(self.expandAll)
        expand_all.setIcon(QIcon(QPixmap('icons/expand-all-button.svg')))
        expand_all.setIconSize(QSize(16, 16))

        collapse_all = QPushButton()
        collapse_all.setIcon(QIcon(QPixmap('icons/collapse-all-button.svg')))
        collapse_all.setIconSize(QSize(16, 16))
        collapse_all.clicked.connect(self.collapseAll)

        button_layout.addWidget(select_all)
        button_layout.addWidget(select_none)
        button_layout.addWidget(expand_all)
        button_layout.addWidget(collapse_all)
        layout.addLayout(button_layout)
        layout.addWidget(self.treeWidget)
        self.setLayout(layout)

    def initModel(self, values: Union[pd.Index, pd.MultiIndex], include_checked=False):
        self.treeWidget.initModel(values, include_checked)

    def getItems(self, selected_only=True) -> List[Tuple]:
        return self.treeWidget.getItems(selected_only)

    def checkAll(self):
        self.treeWidget.checkAll()
        self.itemChecked.emit()

    def checkNone(self):
        self.treeWidget.checkNone()
        self.itemChecked.emit()

    def expandAll(self):
        self.treeWidget.expandAll()

    def collapseAll(self):
        self.treeWidget.collapseAll()


class HierarchicalTreeWidget(QTreeWidget):
    """Widget implementing a tree view of dataframe header"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setHeaderHidden(True)
        # self.itemClicked.connect(self.debug)
        # self.setColumnCount(2)  # in case additional information are needed

    def initModel(self, values: Union[pd.Index, pd.MultiIndex], include_checked=False):
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tree = HierarchicalTreeWidget()
    columns = pd.MultiIndex.from_tuples(
        [(i, f'level_1_{j}', f'level_2_{k}', np.random.randint(0, 2, dtype=bool)) for i in range(2) for j in range(3)
         for k in range(5)])
    # columns = pd.Index(np.arange(10))
    tree.initModel(columns, include_checked=True)

    tree.show()
    sys.exit(app.exec_())
