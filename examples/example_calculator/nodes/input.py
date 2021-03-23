from PyQt5.QtWidgets import QLineEdit, QLabel
from PyQt5.QtCore import Qt
from ..calc_conf import *
from ..calc_node_base import *
from node_editor.utils import dumpException


class CalcInputContent(NodeContentWidget):
    def initUI(self):
        self.edit = QLineEdit("1", self)
        self.edit.setAlignment(Qt.AlignRight)
        self.edit.setObjectName(self.node.content_label_objname)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)
        return res


@register_node(NodeType.OP_NODE_INPUT)
class CalcNode_Input(CalcNode):
    icon = 'resources/in.png'
    op_code = NodeType.OP_NODE_INPUT
    op_title = 'Input'
    content_label = ''
    content_label_objname = 'calc_node_input'

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = CalcInputContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        u_value = self.content.edit.text()
        s_value = int(u_value)
        self.value = s_value

        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantInvalid(False)
        self.markDescendantDirty()

        self.grNode.setToolTip("")

        self.evalChildren()

        return self.value
