import pandas as pd
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal, QSize
from node_editor.utils import dumpException, get_path_relative_to_file

from .tree_widgets import HierarchicalTreeWidget

from typing import Union, Any, List, Tuple

# class DictLike:
#     def __getitem__(self, key):
#         return getattr(self, key)
#
#     def __setitem__(self, key, value):
#         setattr(self, key, value)


# @dataclass
# class Item:
#     state: bool
#     text: str
#     parent:

_RESOURCE_PATH = get_path_relative_to_file(__file__, '../../resources/')


def _get_icon(file_path):
    return QIcon(QPixmap(os.path.join(_RESOURCE_PATH, file_path)))


class TreeWidgetUI(QWidget):
    itemChecked = pyqtSignal()

    def __init__(self, parent=None):
        super(TreeWidgetUI, self).__init__()
        self.treeWidget = HierarchicalTreeWidget(parent)

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        select_all = QPushButton()
        select_all.setIcon(_get_icon('check-all-button.svg'))
        select_all.setIconSize(QSize(16, 16))
        select_all.clicked.connect(self.checkAll)

        select_none = QPushButton()
        select_none.setIcon(_get_icon('check-none-button.svg'))
        select_none.setIconSize(QSize(16, 16))
        select_none.clicked.connect(self.checkNone)

        expand_all = QPushButton()
        expand_all.clicked.connect(self.expandAll)
        expand_all.setIcon(_get_icon('expand-all-button.svg'))
        expand_all.setIconSize(QSize(16, 16))

        collapse_all = QPushButton()
        collapse_all.setIcon(_get_icon('collapse-all-button.svg'))
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


if __name__ == '__main__':
    import sys
    import numpy as np

    app = QApplication(sys.argv)
    tree = HierarchicalTreeWidget()
    columns = pd.MultiIndex.from_tuples(
        [(i, f'level_1_{j}', f'level_2_{k}', np.random.randint(0, 2, dtype=bool)) for i in range(2) for j in range(3)
         for k in range(5)])
    # columns = pd.Index(np.arange(10))
    tree.initModel(columns, include_checked=True)

    tree.show()
    sys.exit(app.exec_())
