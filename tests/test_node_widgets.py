import unittest
import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import *
from data_node_editor.nodes.node_widgets.widgets import *


class TestNodeWidgets(unittest.TestCase):
    """Ran test for node_widget from data_node_editor"""

    def test_checkable_tree_ui(self):
        app = QApplication(sys.argv)
        tree = CheckableTreeWidget()
        columns = pd.MultiIndex.from_tuples(
            [(i, f'level_1_{j}', f'level_2_{k}', np.random.randint(0, 2, dtype=bool)) for i in range(2) for j in
             range(3)
             for k in range(5)])
        tree.initModel(columns, include_checked=True)
        tree.show()

    def test_draggable_widget_ui(self):
        app = QApplication(sys.argv)
        wdg = QWidget()
        upper = DraggableListWidget()
        for n in range(10):
            upper.addItem(ListItem(value=(n, f'item_{n}')))
        lower = DraggableTreeWidget()
        layout = QVBoxLayout()
        layout.addWidget(upper)
        layout.addWidget(lower)

        wdg.setLayout(layout)
        wdg.show()

    def test_embedded_combo_widget_ui(self):
        app = QApplication(sys.argv)
        cmb = ComboBoxOptionItem(options=['option 1', 'option 2', 'option 3'])

        wdg = EmbeddedTreeWidget(defaultWidget=cmb, headers=['options', 'value'])
        wdg.addRootItem('Item 1', widget=cmb)

        wdg.show()

    def test_embedded_list_widget_ui(self):
        app = QApplication(sys.argv)
        cmb = ComboBoxOptionItem(options=['option 1', 'option 2', 'option 3'])

        wdg = EmbeddedListWidget(defaultWidget=cmb)
        wdg.addItem('Item 1', widget=cmb)

        wdg.show()


if __name__ == '__main__':
    unittest.main()
