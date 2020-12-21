from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .node_edge import Edge, EDGE_TYPE_BEZIER
from .node_graphics_socket import OUTPUT_SOCKET, INPUT_SOCKET_1
from .node_graphics_view import QNEGraphicsView
from .node_node import Node
from .node_scene import Scene


class NodeEditorWidget(QWidget):
    """Implement the main window of the app"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.stylesheet_filename = 'qss/nodestyle.qss'
        self.loadStylessheet(self.stylesheet_filename)

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # create graphics scene
        self.scene = Scene()
        # self.grScene = self.scene.grScene
        self.addNodes()

        # create graphics view
        self.view = QNEGraphicsView(self.scene, self)
        # self.view.setScene(self.grScene)
        self.layout.addWidget(self.view)

        # self.addDebugContent()

    def addNodes(self):
        node1 = Node(self.scene, 'My Node', inputs=[INPUT_SOCKET_1] * 3, outputs=[OUTPUT_SOCKET])
        node2 = Node(self.scene, 'My Node', inputs=[INPUT_SOCKET_1] * 3, outputs=[OUTPUT_SOCKET])
        node3 = Node(self.scene, 'My Node', inputs=[INPUT_SOCKET_1] * 3, outputs=[OUTPUT_SOCKET])
        node1.setPos(-350, -250)
        node2.setPos(-75, 0)
        node3.setPos(200, -150)

        edge1 = Edge(self.scene, node1.outputs[0], node2.inputs[0], edge_type=EDGE_TYPE_BEZIER)
        edge2 = Edge(self.scene, node2.outputs[0], node3.inputs[0], edge_type=EDGE_TYPE_BEZIER)

    def addDebugContent(self):
        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.black)
        outlinePen.setWidth(2)

        rect = self.grScene.addRect(-100, -100, 80, 100, outlinePen, greenBrush)
        rect.setFlag(QGraphicsItem.ItemIsMovable)

        text = self.grScene.addText('Blabla', QFont('Ubuntu'))
        text.setFlag(QGraphicsItem.ItemIsSelectable)
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setDefaultTextColor(QColor.fromRgbF(1., 1., 1.))

        widget1 = QPushButton('Hello World')
        proxy1 = self.grScene.addWidget(widget1, )
        proxy1.setFlag(QGraphicsItem.ItemIsMovable)
        proxy1.setPos(0, 30)

        widget2 = QTextEdit()
        proxy2 = self.grScene.addWidget(widget2, )
        proxy2.setFlag(QGraphicsItem.ItemIsSelectable)
        proxy2.setPos(0, 60)

    def loadStylessheet(self, filename):
        print('STYLE loading', filename)
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))
