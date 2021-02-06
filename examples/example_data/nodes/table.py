from PyQt5.QtWidgets import QVBoxLayout, QDialog
from PyQt5.QtCore import Qt
import pandas as pd
from ..data_conf import *
from ..data_node_base import *
from ..data_node_graphics_base import VizGraphicsNode
from node_editor.dataframe_model.datatable_content import DataTableContent, DataEditableTableContent
from node_editor.utils import dumpException
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from node_editor.node_node import Node

DEBUG = True


@NodeFactory.register()
class DataNode_Table(DataNode):
    icon = 'icons/table-64.svg'
    op_title = 'Table'
    content_label = ''
    content_label_objname = 'data_node_table'

    NodeContent_class = DataTableContent
    GraphicsNode_class = VizGraphicsNode

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.min_height = 160
        self.height = 200
        self.min_width = 280
        self.width = 320
        self.grNode.updateLayout()

    def evalImplementation(self):
        self.print('evalImplementation')
        # get first input
        input_node = self.getInput(0)
        if not input_node:
            self.setToolTip('Input is not connected')
            self.markInvalid()
            return

        # get value from input node
        val = input_node.eval()
        if val is None:
            self.setToolTip('Input is NaN')
            self.markInvalid()
            return

        self.value = val
        self.content.setDataFrame(self.value)
        # else set flag and tooltip
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantInvalid(False)
        self.markDescendantDirty()

        self.setToolTip('')

        self.evalChildren()

        # output of the node
        return self.value

    def onDoubleClicked(self, event):
        """Event handling double click on Graphics Node in `Scene`"""
        try:
            flags = Qt.WindowMaximizeButtonHint
            flags |= Qt.WindowCloseButtonHint
            # flags |= Qt.WindowMinimizeButtonHint

            wnd = QDialog(flags=flags)
            layout = QVBoxLayout()
            layout.addWidget(self.content.view.copy())
            wnd.setLayout(layout)
            wnd.exec_()
        except Exception as e:
            dumpException(e)


@NodeFactory.register()
class DataNode_EditableTable(DataNode):
    icon = 'icons/editable-table-64.svg'
    op_title = 'Editable Table'
    content_label = ''
    content_label_objname = 'data_node_editable_table'

    NodeContent_class = DataEditableTableContent
    GraphicsNode_class = VizGraphicsNode

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
        self.content.setDataFrame(pd.DataFrame([[None, None], [None, None]]))
        self.min_height = 160
        self.height = 200
        self.min_width = 280
        self.width = 320
        self.grNode.updateLayout()

    def getDataFrame(self):
        return self.content.view.getDataFrame()

    def evalImplementation(self):
        # Get current content
        self.value = self.getDataFrame()
        self.markDirty(False)
        self.markInvalid(False)
        self.setToolTip('')

        self.evalChildren()
        return self.value
