from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import QRectF
from node_editor.node_node import Node
from node_editor.widgets.node_content_widget import QNENodeContentWidget
from node_editor.node_graphics_node import QNEGraphicsNode
from node_editor.node_socket import LEFT_CENTER, RIGHT_CENTER


class CalcGraphicsNode(QNEGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 74

        # Diverse parameters for drawing
        self.edge_roundness = 6.
        self.edge_padding = 0
        self.title_horizontal_padding = 8.
        self.title_vertical_padding = 10

    def initAssets(self):
        super().initAssets()
        self.icons = QImage('icons/status_icons.png')

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem', widget: QWidget = None) -> None:
        super().paint(painter, option, widget)
        offset = 24.0
        if self.node.isDirty(): offset = 0.
        if self.node.isInvalid(): offset = 48.
        painter.drawImage(QRectF(-10., -10., 24., 24.),
                          self.icons,
                          QRectF(offset, 0, 24., 24.))


class CalcContent(QNENodeContentWidget):
    def initUI(self):
        lbl = QLabel(self.node.content_label, self)
        lbl.setObjectName(self.node.content_label_objname)


class CalcNode(Node):
    icon = ""
    op_code = 0
    op_title = 'Undefined'
    content_label = ''
    content_label_objname = 'calc_node_bg'

    def __init__(self, scene: 'Scene', inputs=[2, 2], outputs=[1]):
        super().__init__(scene, title=self.__class__.op_title, inputs=inputs, outputs=outputs)

    def initInnerClasses(self):
        # Reference to the content
        self.content = CalcContent(self)
        # Reference to the graphic
        self.grNode = CalcGraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        print("Deserialize CalcNode {}: res : {}".format(self.__class__.__name__, res))
        return res
