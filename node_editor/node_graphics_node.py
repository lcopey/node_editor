from PyQt5.QtWidgets import QGraphicsItem, QGraphicsProxyWidget, QGraphicsTextItem, QWidget
from PyQt5.QtGui import QFont, QPen, QColor, QBrush, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QRectF

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .node_node import Node


class QNEGraphicsNode(QGraphicsItem):
    """Implement the graphics version of a node"""

    def __init__(self, node: 'Node', parent=None):
        super().__init__(parent=parent)
        self.node = node  # Reference to parent class Node implementing the logic
        self.content = self.node.content  # Reference to content of the node
        # init flags
        self._was_moved = False
        self._last_selected_state = False

        self.initSizes()
        self.initAssets()
        self.initUI()

    def initUI(self):
        # Define the node as selectable and movable
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        # init _title
        self.initTitle()
        self.title = self.node.title
        # init content
        self.initContent()

    def initSizes(self):
        self.width = 180
        self.height = 240

        # Diverse parameters for drawing
        self.edge_size = 15.
        self.title_height = 24
        self._padding = 5.

    def initAssets(self):
        self._title_color = Qt.white
        self._title_font = QFont('Ubuntu', 8)

        self._pen_default = QPen(QColor("#7F00000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

    def initContent(self):
        # Draw the contents
        self.grContent = QGraphicsProxyWidget(self)
        self.content.setGeometry(self.edge_size, self.title_height + self.edge_size,
                                 self.width - 2 * self.edge_size, self.height - 2 * self.edge_size - self.title_height)
        self.grContent.setWidget(self.content)

    def initTitle(self):
        # Draw the _title
        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = self.node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._padding, 0)
        self.title_item.setTextWidth(self.width - 2 * self._padding)

    def onSelected(self):
        self.node.scene.grScene.itemSelected.emit()

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        # When the node move because of drag
        # update the corresponding edges0
        super().mouseMoveEvent(event)

        # TODO Optimize just update the selected node
        for node in self.scene().scene.nodes:
            if node.grNode.isSelected():
                node.updateConnectedEdges()
        self._was_moved = True

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        # handle when grNode moved
        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.storeHistory('Node moved', setModified=True)

            self.node.scene.resetLastSelectedStates()
            self._last_selected_state = True
            # store the last selected state, because moving also select the node
            self.node.scene._last_selected_items = self.node.scene.getSelectedItems()

            # skip storing selection
            return

        # handle when grNode was clicked on
        # condition met when changing from one selection to another or
        # when multiple items are selected and the current node is then selected
        if self._last_selected_state != self.isSelected() or self.node.scene._last_selected_items != self.node.scene.getSelectedItems():
            # reset all other selected flags to False
            self.node.scene.resetLastSelectedStates()
            # set the new state of this object only
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def boundingRect(self):
        # Return rectangle for selection detection
        return QRectF(0,
                      0,
                      self.width,
                      self.height
                      ).normalized()

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
