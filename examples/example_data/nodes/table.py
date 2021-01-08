from PyQt5.QtWidgets import QLineEdit, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from ..data_conf import *
from ..data_node_base import *
from ..table import DataframeView
from node_editor.utils import dumpException
import pandas as pd

DEBUG = True


class DataTableContent(QNENodeContentWidget):
    def initUI(self):
        df = pd.DataFrame({'a': ['Mary', 'Jim', 'John'],
                           'b': [100, 200, 300],
                           'c': ['a', 'ba', 'c']})

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)
        self.view = DataframeView(dataframe=df, parent=self)
        self.layout.addWidget(self.view)
        self.view.setObjectName(self.node.content_label_objname)

    def print(self, *args):
        print('>DataTableContent :', *args)

    def serialize(self):
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


@register_node(NodeType.OP_NODE_TABLE)
class DataNode_Table(DataNode):
    icon = 'icons/in.png'
    op_code = NodeType.OP_NODE_TABLE
    op_title = 'Table'
    content_label = ''
    content_label_objname = 'data_node_table'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[3])
        self.eval()
        self.min_height = 160
        self.height = 200
        self.min_width = 280
        self.width = 320
        self.grNode.updateLayout()

    def initInnerClasses(self):
        self.content = DataTableContent(self)
        self.grNode = DataGraphicsNode(self)
        self.print('initInnerClasses done')
        # self.content.edit.textChanged.connect(self.onInputChanged)

    def print(self, *args):
        if DEBUG: print('>DataNode_Table : ', *args)
    #
    # def evalImplementation(self):
    #     u_value = self.content.edit.text()
    #     s_value = int(u_value)
    #     self.value = s_value
    #
    #     self.markDirty(False)
    #     self.markInvalid(False)
    #
    #     self.markDescendantInvalid(False)
    #     self.markDescendantDirty()
    #
    #     self.grNode.setToolTip("")
    #
    #     self.evalChildren()
    #
    #     return self.value
