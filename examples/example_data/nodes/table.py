from PyQt5.QtWidgets import QLineEdit, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
import pandas as pd
from ..data_conf import *
from ..data_node_base import *
from ..table_model import DataframeView
from node_editor.utils import dumpException
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from node_editor.node_node import Node
    from PyQt5.QtWidgets import QWidget

DEBUG = True


class DataTableContent(NodeContentWidget):
    def __init__(self, node: 'Node', parent: QWidget = None, editable=False):
        self.editable = editable
        super().__init__(node, parent)

    def initUI(self):
        df = pd.DataFrame()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)
        self.view = DataframeView(dataframe=df, parent=self, editable=self.editable)
        self.layout.addWidget(self.view)
        self.view.setObjectName(self.node.content_label_objname)

    def print(self, *args):
        if DEBUG:
            print('>DataTableContent :', *args)

    def setDataFrame(self, dataframe: pd.DataFrame):
        self.view.setDataFrame(dataframe, editable=self.editable)

    def getDataFrame(self):
        return self.view.getDataFrame()

    def serialize(self):
        # must return a value otherwise crash on deserialize
        self.print('serialize')
        return 0
    #
    # def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True):
    #     res = super().deserialize(data, hashmap)
    #     try:
    #         value = data['value']
    #         self.edit.setText(value)
    #         return True & res
    #     except Exception as e:
    #         dumpException(e)
    #     return res


class DataEditableTableContent(DataTableContent):
    def __init__(self, node: 'Node', parent: QWidget = None):
        super().__init__(node, parent, editable=True)


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

        # else set flag and tooltip
        self.markDirty(False)
        self.markInvalid(False)
        self.setToolTip('')
        self.value = val
        self.content.setDataFrame(self.value)

        # output of the node
        return self.content.getDataFrame()


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
