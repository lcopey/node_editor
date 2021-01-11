from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .node_graphics_edge_path import QNEGraphicsEdgePathBezier, QNEGraphicsEdgePathDirect

EDGE_WIDTH = 3.


import typing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node_edge import Edge


class GraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge: 'Edge', parent=None):
        super().__init__(parent)

        self.edge = edge  # link to the Edge class implementing the logic

        # instance of path class
        self.pathCalculator = self.determineEdgePathClass()(self)
        # init flags
        self._last_selected_state = False
        self.hovered = False

        # init variables
        self.posSource = [0, 0]
        self.posDestination = [0, 0]

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

    def createEdgePathCalculator(self):
        self.pathCalculator = self.determineEdgePathClass()(self)
        return self.pathCalculator

    def determineEdgePathClass(self):
        from .node_edge import EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT
        if self.edge.edge_type == EDGE_TYPE_DIRECT:
            return QNEGraphicsEdgePathDirect
        else:
            return QNEGraphicsEdgePathBezier

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
        return self.pathCalculator.calcPath()

    def intersectsWith(self, p1, p2):
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calcPath()
        return cutpath.intersects(path)


