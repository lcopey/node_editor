from PyQt5.QtWidgets import QWidget, QStyleOptionGraphicsItem
from PyQt5.QtGui import QPainter, QPainterPath
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontMetrics
from PyQt5.QtCore import Qt
from math import sin, cos, radians, pi
from node_editor.node_graphics_node import GraphicsNode
from node_editor.node_node import Node
from node_editor.node_socket import SocketPosition
from typing import Optional, List


class VizGraphicsNode(GraphicsNode):
    def __init__(self, node: 'Node', parent=None):
        super().__init__(node=node, parent=parent, resizeable=True, min_width=160, width=160, min_height=74, height=74)
        # Diverse parameters for drawing
        self.edge_roundness = 6.
        self.edge_padding = 0
        self.title_horizontal_padding = 8.
        self.title_vertical_padding = 10


class OpGraphicsNode(GraphicsNode):
    def __init__(self, node: 'Node', parent=None):
        super().__init__(node=node, parent=parent, resizeable=False, min_width=70, width=70, min_height=54, height=54)
        # Diverse parameters for drawing
        self.edge_roundness = 6.
        self.edge_padding = 0
        self.title_horizontal_padding = 8.
        self.title_vertical_padding = 10

    # Define a new property relative to currently implemented height
    @property
    def radius(self):
        return self.rect().height() / 2

    @radius.setter
    def radius(self, value):
        self.height = value * 2

    def getSocketPosition(self, index: int, position: SocketPosition, num_out_of: int = 1) -> List[float]:
        """Overrides default :class:`~node_editor.node_node.GraphicalNode` getSocketPosition to position the socket on
        the circular node."""
        # Which side
        if position in (SocketPosition.TopLeft, SocketPosition.MiddleLeft, SocketPosition.BottomLeft):
            left = True
        else:
            left = False

        # maximum angle between two socket set to 25 for 2 sockets, 20 for 3, 15 for 4
        d_theta = -5 * num_out_of + 35
        if num_out_of == 1:
            socket_angle = 0
        else:
            max_theta = (num_out_of - 1) * radians(d_theta)
            socket_angle = max_theta - index * (2 * max_theta / (num_out_of - 1))

        if left:
            x = self.radius * (1 - cos(socket_angle))
            y = self.radius * (1 + sin(-socket_angle))
        else:
            x = self.radius * (1 + cos(socket_angle))
            y = self.radius * (1 + sin(socket_angle))
        return [x, y]

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem',
              widget: Optional[QWidget] = ...) -> None:
        """Paint the node as filled circle of radius equal to heigth / 2

        Parameters
        ----------
        painter : QPainter
        option : QStyleOptionGraphicsItem
        widget : QWidget

        Returns
        -------
        None
        """
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        path_content.addEllipse(0, 0, 2 * self.radius, 2 * self.radius)
        painter.drawPath(path_content)

        # outline
        path_outline = QPainterPath()
        path_outline.addEllipse(0, 0, 2 * self.radius, 2 * self.radius)
        painter.setBrush(Qt.NoBrush)
        if self._hovered:
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
            painter.drawPath(path_outline.simplified())
