from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QWidget
from PyQt5.QtCore import Qt
import pandas as pd
from ..data_conf import *
from ..data_node_base import *
from ..data_node_graphics_base import OpGraphicsNode
from node_editor.widgets import TreeWidgetUI
from typing import TYPE_CHECKING, Union, List, Tuple, Any

if TYPE_CHECKING:
    from node_editor.node_node import Node
    from PyQt5.QtWidgets import QWidget

DEBUG = True


@NodeFactory.register()
class DataNode_SelectColumns(DataNode):
    icon = 'icons/table-select-columns-64.svg'
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
        self.treeWidget = TreeWidgetUI()
        self.treeWidget.itemChecked.connect(self.forcedEval)
        # self.treeWidget = HierarchicalTreeWidget()
        # # changing item clicked triggers markdirty and evaluation of the node
        # self.treeWidget.itemClicked.connect(self.forcedEval)
        #
        layout = QVBoxLayout()
        # button_layout = QHBoxLayout()
        #
        # select_all = QPushButton('Select All')
        # select_all.clicked.connect(self.selectAll)
        #
        # select_none = QPushButton('Select None')
        # select_none.clicked.connect(self.selectNone)
        #
        # button_layout.addWidget(select_all)
        # button_layout.addWidget(select_none)
        # layout.addLayout(button_layout)
        layout.addWidget(self.treeWidget)
        self.propertiesWidget.setLayout(layout)

    # def selectAll(self):
    #     """Select all item in `listWidget` attributes"""
    #     self.treeWidget.checkAll()
    #     self.forcedEval()
    #
    # def selectNone(self):
    #     """Unselect all item in `listWidget` attributes"""
    #     self.treeWidget.checkNone()
    #     self.forcedEval()

    def updatePropertiesWidget(self):
        """Populate `listWidget` with values from input dataframe columns"""
        if self.columns is not None:
            self.treeWidget.initModel(self.columns)

    def getColumnSelection(self) -> List[Union[Tuple, Any]]:
        # TODO Handle index type
        """Returns a list of checked columns

        Returns
        -------
        list[Union[tuple, Any]]
            list of checked column name
        """
        return self.treeWidget.getItems()

    def evalImplementation(self, force=False):
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

    # def serialize(self):
    #     result = super().serialize()
    #
    #     state = {}
    #     # save the the state of the properties dock widget
    #     # for n in range(self.listWidget.count()):
    #     #     item = self.listWidget.item(n)
    #     #     state[item.text()] = item.checkState() == Qt.Checked
    #     result['state'] = state
    #     return result
    #
    # def deserialize(self, data, hashmap=None, restore_id=True):
    #     # TODO Fix
    #     result = super().deserialize(data, hashmap, restore_id)
    #     # If connected restore the values of the properties widget and evaluate
    #     if self.getInput(0):
    #         for key, value in result['state'].items():
    #             # restore the state of the properties dock widget
    #             # item = QListWidgetItem()
    #             # item.setText(str(key))
    #             # item.setCheckState(Qt.Checked if value else Qt.Unchecked)
    #             # self.listWidget.addItem(item)
    #             pass
