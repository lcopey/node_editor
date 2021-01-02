from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import math

EDGE_WIDTH = 3.
EDGE_CP_ROUNDNESS = 100

import typing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node_edge import Edge


class QNEGraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge: 'Edge', parent=None):
        super().__init__(parent)

        self.edge = edge  # link to the Edge class implementing the logic
        # init flags
        self._last_selected_state = False
        self.hovered = False
        # self.posSource = [0, 0]
        # self.posDestination = [0, 0]

        self.initAssets()
        self.initUI()

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)

    def initAssets(self):
        """Initialize assets ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        # Diverse parameters for drawing
        self._color = self._default_color = QColor("#001000")
        self._color_selected = QColor("#00ff00")
        self._color_hovered = QColor("#FF37A6FF")

        self._pen = QPen(self._color)
        self._pen.setWidthF(EDGE_WIDTH)

        self._pen_selected = QPen(self._color_selected)
        self._pen.setWidthF(EDGE_WIDTH)

        self._pen_dragging = QPen(self._color)
        self._pen_dragging.setWidthF(EDGE_WIDTH)
        self._pen_dragging.setStyle(Qt.DashLine)

        self._pen_hovered = QPen(self._color_hovered)
        self._pen_hovered.setWidthF(EDGE_WIDTH + 2.)

    def changeColor(self, color):
        """Change the color of the `Edge`

        Parameters
        ----------
        color : `QColor` or str
            Either a valid `QColor` or ``str`` such as #001000
        """
        if type(color) == str:
            self._color = QColor(color)
        elif isinstance(color, QColor):
            self._color = color
        else:
            return
        self._pen = QPen(self._color)
        self._pen.setWidthF(EDGE_WIDTH)

    def setColorFromSockets(self) -> bool:
        """Change color according to connected sockets. Return ```True``` if color can be determined"""
        socket_type_start = self.edge.start_socket.socket_type
        socket_type_end = self.edge.end_socket.socket_type
        if socket_type_start != socket_type_end: return False
        self.changeColor(self.edge.start_socket.grSocket.getSocketColor(socket_type_start))
        return True

    def onSelected(self):
        self.edge.scene.grScene.itemSelected.emit()

    def doSelect(self, new_state=True):
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state:
            self.onSelected()

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseReleaseEvent(event)
        if self._last_selected_state != self.isSelected():
            # reset all other selected flags to False
            self.edge.scene.resetLastSelectedStates()
            # set the new state of this object only
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = False
        self.update()

    def setSource(self, x, y):
        """Set itinial position of the edge to x, y"""
        self.posSource = (x, y)

    def setDestination(self, x, y):
        """Set end position of the edge to x, y"""
        self.posDestination = (x, y)

    def boundingRect(self) -> QRectF:
        return self.shape().boundingRect()

    def shape(self) -> QPainterPath:
        return self.calcPath()

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...) -> None:
        """Overrides default paint method if QGraphicsItem.

        Compute path of the edge, select pen depending on :
            are we in dragging mode
            is the edge selected or not
        """
        path = self.calcPath()
        self.setPath(path)

        # hover effect
        if self.hovered and self.edge.end_socket is not None:
            painter.setPen(self._pen_hovered)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self.path())

        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def calcPath(self):
        """Will handle drawing QPainterPath from Paint A to B"""
        raise NotImplemented("This method has to be overriden in a child class")

    def intersectsWith(self, p1, p2):
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calcPath()
        return cutpath.intersects(path)


class QNEGraphicsEdgeDirect(QNEGraphicsEdge):
    def calcPath(self):
        """Compute linear path from source to destination"""
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])
        return path


class QNEGraphicsEdgeBezier(QNEGraphicsEdge):
    def calcPath(self):
        """Compute bezier curves from source to destination"""
        s = self.posSource
        d = self.posDestination

        dist = (d[0] - s[0]) * 0.5

        # Compute control point
        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if self.edge.start_socket is not None:
            ssin = self.edge.start_socket.is_input
            ssout = self.edge.start_socket.is_output
            sspos = self.edge.start_socket.position
            if (s[0] > d[0] and ssout) or (s[0] < d[0] and ssin):
                cpx_d *= -1
                cpx_s *= -1

                cpy_d = ((s[1] - d[1]) / (math.fabs(s[1] - d[1]) + 1e-8)) * EDGE_CP_ROUNDNESS
                cpy_s = ((d[1] - s[1]) / (math.fabs(s[1] - d[1]) + 1e-8)) * EDGE_CP_ROUNDNESS

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.cubicTo(s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d,
                     self.posDestination[0], self.posDestination[1])
        return path
