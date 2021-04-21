from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QWidget
from PyQt5.QtCore import Qt
import pandas as pd
from ..data_conf import *
from ..data_node_base import DataNode, Configurable
from ..data_node_graphics_base import OpGraphicsNode
from .node_widgets import CheckableTreeUI
from typing import TYPE_CHECKING, Union, List, Tuple, Any

if TYPE_CHECKING:
    from node_editor.node_node import Node
    from PyQt5.QtWidgets import QWidget

DEBUG = True


@NodeFactory.register()
class DataNode_SelectColumns(DataNode, Configurable):
    icon = 'resources/table-select-columns-64.svg'
    op_title = 'Select Columns'
    content_label = ''
    content_label_objname = 'data_node_select_columns'

    # NodeContent_class = DataTableContent
    GraphicsNode_class = OpGraphicsNode

    def __init__(self, scene):
        self.columns = None
        super().__init__(scene, inputs=[1], outputs=[1])

    def initPropertiesWidget(self):
        """Initialize the layout of properties DockWidget"""
        self.propertiesWidget = QWidget()
        # widget holding the column name
        self.treeWidget = CheckableTreeUI()
        self.treeWidget.itemChecked.connect(self.forcedEval)

        layout = QVBoxLayout()
        layout.addWidget(self.treeWidget)
        self.propertiesWidget.setLayout(layout)

    def updatePropertiesWidget(self):
        """Populate `listWidget` with values from input dataframe columns"""
        if self.columns is not None:
            self.treeWidget.initModel(self.columns)

    def getColumnSelection(self) -> List[Union[Tuple, Any]]:
        """Returns a list of checked columns

        Returns
        -------
        list[Union[tuple, Any]]
            list of checked column name
        """
        return self.treeWidget.getItems()

    def evalImplementation(self, force: bool = False):
        self.print('evalImplementation')

        # get first input
        input_node = self.getInput(0)
        if not input_node:
            self.setToolTip('Input is not connected')
            self.markInvalid()
            return

        # get value from input node
        self.input_val = input_node.eval()
        if isinstance(self.input_val, pd.DataFrame):
            new_columns = self.input_val.columns
        else:
            self.columns = None
            new_columns = None

        # Compare if new columns are the same as the old one
        if self.columns is None or not (self.columns.equals(new_columns)):
            # Update the properties toolbar accordingly
            self.columns = new_columns
            self.updatePropertiesWidget()

        if self.columns is None:
            self.setToolTip('Input is NaN')
            self.markInvalid()
            return

        # Store the table with only the selected columns
        column_selection = self.getColumnSelection()
        if column_selection:
            self.value = self.input_val[column_selection]
        else:
            self.value = pd.DataFrame()

        # else set flag and tooltip
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantInvalid(False)
        self.markDescendantDirty()

        self.setToolTip('')

        self.evalChildren()

        return self.value

    def getNodeSettings(self) -> dict:
        return {'items': self.treeWidget.getItems(selected_only=False)}

    def restoreNodeSettings(self, data: dict) -> bool:
        kwargs = data['node_settings']
        self.treeWidget.initModel(kwargs['items'], include_checked=True)
        return True
