from PyQt5.QtWidgets import QVBoxLayout, QDialog
from PyQt5.QtCore import Qt
import pandas as pd
import numpy as np
from ..data_conf import *
from ..data_node_base import *
from ..data_node_graphics_base import VizGraphicsNode
from node_editor.dataframe_model import DataFrameView, DataTableView
from node_editor.node_content_widget import NodeContentWidget
# from node_editor.dataframe_model_bak.datatable_content import DataTableContent, DataEditableTableContent
from node_editor.utils import dumpException
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from node_editor.node_node import Node

DEBUG = True


class DataTableContent(NodeContentWidget):
    def __init__(self, node: 'Node', parent: 'QWidget' = None):
        self.view: DataFrameView
        super().__init__(node, parent)

    def initUI(self):
        # df = pd.DataFrame()
        # TODO for debug purpose only
        # df = pd.DataFrame(np.random.rand(20, 3))
        index = pd.MultiIndex.from_tuples(
            [(f'level_0_{i}', f'level_1_{j}', f'level_2_{k}') for i in range(2) for j in range(3) for k in range(5)])
        df = pd.DataFrame(np.random.rand(3, len(index)).T, index=index)
        # Define layout including the DataFrameView
        self.layout = QVBoxLayout()
        # self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        # self.view = DataTableView(dataframe=df, parent=self)
        self.view = DataFrameView(dataframe=df, parent=self)
        self.layout.addWidget(self.view)
        self.view.setObjectName(self.node.content_label_objname)

    def print(self, *args):
        if DEBUG:
            print('>DataTableContent :', *args)

    def setDataFrame(self, dataframe: pd.DataFrame):
        self.view.setDataFrame(dataframe, )

    @property
    def dataframe(self):
        return self.view.dataframe

    def serialize(self):
        # must return a value otherwise crash on deserialize
        self.print('serialize')
        return 0


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

    # NodeContent_class = DataEditableTableContent
    # TODO temporary fix
    NodeContent_class = DataTableContent
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
