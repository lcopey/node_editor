from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .node_node import Node


class QNEGraphicsNode(QGraphicsItem):
    """Implement the graphics version of a node"""

    def __init__(self, node: 'Node', parent=None):
        super().__init__(parent=parent)
        self.node = node  # Reference to parent class Node implementing the logic
        self.content = self.node.content  # Reference to content of the node

        # Diverse parameters for drawing
        self._title_color = Qt.white
        self._title_font = QFont('Ubuntu', 10)
        self.title_height = 24
        self._padding = 5.

        self.width = 180
        self.height = 240
        self.edge_size = 15.

        self._pen_default = QPen(QColor("#7F00000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        # init _title
        self.initTitle()
        self.title = self.node.title
        # init content
        self.initContent()
        self.initUI()
        self.wasMoved = False

    def initUI(self):
        # Define the node as selectable and movable
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def initContent(self):
        # Draw the contents
        self.grContent = QGraphicsProxyWidget(self)
        self.content.setGeometry(self.edge_size, self.title_height + self.edge_size,
                                 self.width - 2 * self.edge_size, self.height - 2 * self.edge_size - self.title_height)
        self.grContent.setWidget(self.content)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        # When the node move because of drag
        # update the corresponding edges0
        super().mouseMoveEvent(event)

        # TODO Optimize just update the selected node
        for node in self.scene().scene.nodes:
            if node.grNode.isSelected():
                node.updateConnectedEdges()
        self.wasMoved = True

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.wasMoved:
            self.wasMoved = False
            self.node.scene.history.storeHistory('Node moved', setModified=True)

    def boundingRect(self):
        # Return rectangle for selection detection
        return QRectF(0,
                      0,
                      self.width,
                      self.height
                      ).normalized()

    def initTitle(self):
        # Draw the _title
        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = self.node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._padding, 0)
        self.title_item.setTextWidth(self.width - 2 * self._padding)

    @property
    def title(self, ):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem',
              widget: Optional[QWidget] = ...) -> None:
        # _title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, self.edge_size, self.edge_size)
        path_title.addRect(0, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, self.title_height - self.edge_size, self.edge_size,
                           self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_size,
                                    self.edge_size)
        path_content.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.title_height, self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())
