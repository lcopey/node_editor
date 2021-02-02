from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPainterPath
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontMetrics
from PyQt5.QtCore import Qt
from node_editor.node_graphics_node import GraphicsNode
from node_editor.node_node import Node
from typing import Optional


class VizGraphicsNode(GraphicsNode):
    def __init__(self, node: 'Node', parent=None):
        super().__init__(node=node, parent=parent, resizeable=True, min_width=160, width=160, min_height=74, height=74)
        # Diverse parameters for drawing
        self.edge_roundness = 6.
        self.edge_padding = 0
        self.title_horizontal_padding = 8.
        self.title_vertical_padding = 10


class OpGraphicsNode(GraphicsNode):
    # TODO subclass paint as a circle
    # TODO subclass getSocketPosition
    def __init__(self, node: 'Node', parent=None):
        super().__init__(node=node, parent=parent, resizeable=False, min_width=70, width=70, min_height=54, height=54)
        # Diverse parameters for drawing
        self.edge_roundness = 6.
        self.edge_padding = 0
        self.title_horizontal_padding = 8.
        self.title_vertical_padding = 10

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem',
              widget: Optional[QWidget] = ...) -> None:

        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        radius = self.height / 2
        path_content.addEllipse(0, 0, 2 * radius, 2 * radius)
        painter.drawPath(path_content)

        # outline
        path_outline = QPainterPath()
        path_outline.addEllipse(0, 0, 2 * radius, 2 * radius)
        painter.setBrush(Qt.NoBrush)
        if self._hovered:
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
            painter.drawPath(path_outline.simplified())
