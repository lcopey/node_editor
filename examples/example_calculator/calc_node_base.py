from PyQt5.QtWidgets import QLabel
from node_editor.node_node import Node
from node_editor.widgets.node_content_widget import QNENodeContentWidget
from node_editor.node_graphics_node import QNEGraphicsNode


class CalcGraphicsNode(QNEGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 74

        # Diverse parameters for drawing
        self.edge_size = 5.
        self._padding = 8.


class CalcContent(QNENodeContentWidget):
    def initUI(self):
        lbl = QLabel(self.node.content_label, self)
        lbl.setObjectName(self.node.content_label_objname)


class CalcNode(Node):
    def __init__(self, scene: 'Scene', op_code, op_title, content_label="", content_label_objname="calc_node_bg",
                 inputs=[2, 2], outputs=[1]):
        self.op_code = op_code
        self.op_title = op_title
        self.content_label = content_label
        self.content_label_objname = content_label_objname
        super().__init__(scene, title=op_title, inputs=inputs, outputs=outputs)

    def initInnerClasses(self):
        # Reference to the content
        self.content = CalcContent(self)
        # Reference to the graphic
        self.grNode = CalcGraphicsNode(self)
