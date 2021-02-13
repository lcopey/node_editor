from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget, QApplication
from PyQt5.QtCore import Qt, QRectF, QPointF, QPoint
from PyQt5.QtGui import QFont, QPen, QColor, QBrush, QPainter, QPainterPath
from .utils import dumpException
from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .node_graphics_node import GraphicsNode
    from PyQt5.QtWidgets import QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent


class HandlePosition(Enum):
    TopLeft = 1
    TopMiddle = 2
    TopRight = 3
    MiddleLeft = 4
    MiddleRight = 5
    BottomLeft = 6
    BottomMiddle = 7
    BottomRight = 8


class HandleMode(Enum):
    NOOP = 1
    DRAG = 2


handleUpdate = {
    HandlePosition.TopLeft: (True, True, False, False),
    HandlePosition.TopMiddle: (False, True, False, False),
    HandlePosition.TopRight: (False, True, True, False),
    HandlePosition.MiddleLeft: (True, False, False, False),
    HandlePosition.MiddleRight: (False, False, True, False),
    HandlePosition.BottomLeft: (True, False, False, True),
    HandlePosition.BottomMiddle: (False, False, False, True),
    HandlePosition.BottomRight: (False, False, True, True),
}

handleCursors = {
    HandlePosition.TopLeft: Qt.SizeFDiagCursor,
    HandlePosition.TopMiddle: Qt.SizeVerCursor,
    HandlePosition.TopRight: Qt.SizeBDiagCursor,
    HandlePosition.MiddleLeft: Qt.SizeHorCursor,
    HandlePosition.MiddleRight: Qt.SizeHorCursor,
    HandlePosition.BottomLeft: Qt.SizeBDiagCursor,
    HandlePosition.BottomMiddle: Qt.SizeVerCursor,
    HandlePosition.BottomRight: Qt.SizeFDiagCursor,
}

DEBUG = True


class Handle(QGraphicsItem):
    def __init__(self, grNode: 'GraphicsNode', position: HandlePosition):
        super().__init__(parent=grNode)
        self.grNode = grNode
        self.position = position
        self.handleSize = 8
        self._offset = 4
        self._hovered = False
        self.setAcceptHoverEvents(True)
        self.mode = HandleMode.NOOP
        self._color = QColor("#7F00000")
        self._color_hovered = QColor("#FF37A6FF")
        self._pen_default = QPen(self._color)
        self._pen_default.setWidthF(1.)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_hovered.setWidthF(1. + 1)
        self.setHandlePosition()

    @property
    def width(self):
        try:
            if self.position in [HandlePosition.TopMiddle, HandlePosition.BottomMiddle]:
                return self.grNode.width - 2 * self.handleSize
            else:
                return self.handleSize

        except Exception as e:
            dumpException(e)

    @property
    def height(self):
        try:
            if self.position in [HandlePosition.MiddleLeft, HandlePosition.MiddleRight]:
                return self.grNode.height - 2 * self.handleSize
            else:
                return self.handleSize
        except Exception as e:
            dumpException(e)

    def setHandlePosition(self):
        if self.grNode is not None:
            if self.position in (HandlePosition.TopLeft, HandlePosition.MiddleLeft, HandlePosition.BottomLeft):
                x = -self._offset
            elif self.position in (HandlePosition.TopRight, HandlePosition.MiddleRight, HandlePosition.BottomRight):
                x = self.grNode.width - self.handleSize + self._offset
            else:
                x = self.handleSize

            if self.position in (HandlePosition.TopLeft, HandlePosition.TopMiddle, HandlePosition.TopRight):
                y = -self._offset
            elif self.position in (HandlePosition.BottomLeft, HandlePosition.BottomMiddle, HandlePosition.BottomRight):
                y = self.grNode.height - self.handleSize + self._offset
            else:
                y = self.handleSize

            self.setPos(x, y)
        else:
            print('Exception : Handle without node')

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.changeCursorOnHover()

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.changeCursorOnHover()

    def changeCursorOnHover(self, ):
        self._hovered = True
        self.setCursor(handleCursors[self.position])
        self.update()

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self._hovered = False
        self.setCursor(Qt.ArrowCursor)
        self.update()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.mode == HandleMode.NOOP:
            self._currentPos = event.pos()
            self._currentRect = self.grNode.boundingRect()
            self.mode = HandleMode.DRAG

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.mode == HandleMode.DRAG:
            pos = event.pos()

            from_left = self._currentRect.left()
            from_right = self._currentRect.right()
            from_top = self._currentRect.top()
            from_bottom = self._currentRect.bottom()
            to_left = from_left + pos.x() - self._currentPos.x()
            to_right = from_right + pos.x() - self._currentPos.x()
            to_top = from_top + pos.y() - self._currentPos.y()
            to_bottom = from_bottom + pos.y() - self._currentPos.y()
            update_left, update_top, update_right, update_bottom = handleUpdate[self.position]
            rect = self.grNode.rect()
            if update_left:
                rect.setLeft(to_left)
            if update_top:
                rect.setTop(to_top)
            if update_bottom:
                rect.setBottom(to_bottom)
            if update_right:
                rect.setRight(to_right)

            self.grNode.resize(rect)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.mode == HandleMode.DRAG:
            self.grNode.updateHandles()
            self.mode = HandleMode.NOOP

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height).normalized()

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem', widget: Optional[QWidget] = ...) -> None:
        if DEBUG:
            painter.setPen(self._pen_hovered if self.mode == HandleMode.DRAG else self._pen_default)
            painter.setBrush(Qt.NoBrush)
            path = QPainterPath()
            path.addRect(0, 0, self.width, self.height)
            painter.drawPath(path)
