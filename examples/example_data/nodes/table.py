from PyQt5.QtWidgets import QLineEdit, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from ..data_conf import *
from ..data_node_base import *
from ..table import DataframeView
from node_editor.utils import dumpException
import pandas as pd


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

    # def serialize(self):
    #     res = super().serialize()
    #     res['value'] = self.edit.text()
    #     return res
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
class DataNode_Table(CalcNode):
    icon = 'icons/in.png'
    op_code = NodeType.OP_NODE_TABLE
    op_title = 'Table'
    content_label = ''
    content_label_objname = 'data_node_table'

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])
        self.eval()
        self.min_height = 160
        self.height = 160
        self.min_width = 280
        self.width = 280
        self.grNode.updateLayout()

    def initInnerClasses(self):
        self.content = DataTableContent(self)
        self.grNode = DataGraphicsNode(self)
        # self.content.edit.textChanged.connect(self.onInputChanged)
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
