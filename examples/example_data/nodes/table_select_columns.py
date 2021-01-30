from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout, QDialog, QListWidget, QListWidgetItem, QScrollArea, \
    QWidget, QPushButton
from PyQt5.QtCore import Qt
import pandas as pd
from ..table_model.dataframe_view import DataframeView
from ..data_conf import *
from ..data_node_base import *
from ..data_node_graphics_base import OpGraphicsNode
from ..table_model.datatable_content import DataTableContent, DataEditableTableContent
from node_editor.utils import dumpException
from typing import TYPE_CHECKING

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

    def initPropertiesToolbar(self):
        # TODO displace in content ?
        """Initialize the layout of properties DockWidget"""
        self.properties_toolbar = QWidget()
        self.listWidget = QListWidget()
        # changing item clicked triggers markdirty and evaluation of the node
        self.listWidget.itemClicked.connect(self.onItemClicked)
        self.fillListWidget()

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        select_all = QPushButton('Select All')
        select_all.clicked.connect(self.selectAll)

        select_none = QPushButton('Select None')
        select_none.clicked.connect(self.selectNone)

        button_layout.addWidget(select_all)
        button_layout.addWidget(select_none)
        layout.addLayout(button_layout)
        layout.addWidget(self.listWidget)
        self.properties_toolbar.setLayout(layout)

    def selectAll(self):
        """Select all item in `listWidget` attributes"""
        for n in range(self.listWidget.count()):
            item = self.listWidget.item(n)
            item.setCheckState(Qt.Checked)
        self.onItemClicked()

    def selectNone(self):
        """Unselect all item in `listWidget` attributes"""
        for n in range(self.listWidget.count()):
            item = self.listWidget.item(n)
            item.setCheckState(Qt.Unchecked)
        self.onItemClicked()

    def fillListWidget(self):
        """Fill `listWidget` with values from input dataframe columns"""
        self.listWidget.clear()
        if self.columns is not None:
            for column in self.columns:
                item = QListWidgetItem()
                item.setText(str(column))
                item.setCheckState(Qt.Checked)

                self.listWidget.addItem(item)

    def getPropertiesToolbar(self):
        """Return the widget to display properties dock widget"""
        return self.properties_toolbar

    def onItemClicked(self):
        """On Item Clicked event

        Update the selection and evaluate the children `Nodes`
        """
        # Store the table with only the selected columns
        self.updateValue()

        # if self.getOutputs():
        self.markChildrenDirty()
        self.evalChildren()

    def getColumnSelection(self) -> list[str]:
        # TODO Handle index type
        """Returns a list of checked columns

        Returns
        -------
        list[str]
            list of checked column name
        """
        result = []
        for n in range(self.listWidget.count()):
            item = self.listWidget.item(n)
            if item.checkState() == Qt.Checked:
                result.append(item.text())

        return result

    def updateValue(self):
        """Update self.value with the current selection"""
        # Store the table with only the selected columns
        column_selection = self.getColumnSelection()
        if column_selection:
            self.value = self.input_val[column_selection]
        else:
            self.value = pd.DataFrame()

    def evalImplementation(self):
        self.print('evalImplementation')

        self.markDirty(False)
        self.markInvalid(False)

        # get first input
        input_node = self.getInput(0)
        if not input_node:
            self.setToolTip('Input is not connected')
            self.markInvalid()
            return

        # get value from input node
        self.input_val = input_node.eval()
        if isinstance(self.input_val, pd.DataFrame):
            columns = self.input_val.columns
        else:
            self.columns = None
            columns = None

        if self.columns is None or (self.columns != columns).any():
            # Compare if different
            # Update the properties toolbar accordingly
            self.columns = columns
            self.fillListWidget()

        if self.columns is None:
            self.setToolTip('Input is NaN')
            self.markInvalid()
            return

        # Store the table with only the selected columns
        self.updateValue()

        # else set flag and tooltip
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantInvalid(False)
        self.markDescendantDirty()

        self.setToolTip('')

        self.evalChildren()

        return self.value

    def serialize(self):
        result = super().serialize()

        state = {}
        for n in range(self.listWidget.count()):
            item = self.listWidget.item(n)
            state[item.text()] = item.checkState() == Qt.Checked
        result['state'] = state
        return result

    def deserialize(self, data, hashmap=None, restore_id=True):
        # TODO Fix
        result = super().deserialize(data, hashmap, restore_id)
        # If connected restore the values of the properties widget and evaluate
        if self.getInput(0):
            for key, value in result['state']:
                item = QListWidgetItem()
                item.setText(str(key))
                item.setCheckState(Qt.Checked if value else Qt.Unchecked)
                self.listWidget.addItem(item)
