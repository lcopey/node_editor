from PyQt5.QtCore import Qt
from ..calc_conf import *
from ..calc_node_base import *
from node_editor.utils import dumpException


class CalcOutputContent(QNENodeContentWidget):
    def initUI(self):
        self.lbl = QLabel("42", self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setObjectName(self.node.content_label_objname)


@register_node(NodeType.OP_NODE_OUTPUT)
class CalcNodeOutput(CalcNode):
    icon = 'icons/out.png'
    op_code = NodeType.OP_NODE_OUTPUT
    op_title = 'Output'
    content_label = ''
    content_label_objname = 'calc_node_output'

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])

    def initInnerClasses(self):
        self.content = CalcOutputContent(self)
        self.grNode = CalcGraphicsNode(self)

    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip('Input is not connected')
            self.markInvalid()
            return

        val = input_node.eval()
        if val is None:
            self.grNode.setToolTip('Input is NaN')
            self.markInvalid()
            return

        self.content.lbl.setText('{}'.format(val))
        self.markDirty(False)
        self.markInvalid(False)
        self.grNode.setToolTip('')

        return val
