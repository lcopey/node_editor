from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QBrush, QPainterPath, QPainter, QColor, QPen, QFont
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsItem, QWidget, QVBoxLayout, QGraphicsSceneMouseEvent, \
    QGraphicsSceneHoverEvent, QStyleOptionGraphicsItem, QLabel, QTextEdit, QGraphicsProxyWidget, QGraphicsTextItem
from node_editor.node_content_widget import NodeContentWidget

from .const import Handle, handleCursors, handleUpdate
from typing import Optional

from node_editor.utils import print_func_name

DEBUG = False

OUTLINE_WIDTH = 1.0


class QGraphicsResizableRectItem(QGraphicsRectItem):
    def __init__(self, min_height, min_width, *args):
        super().__init__(*args)
        # Diverse parameters for drawing

        self.handleSelected = None
        self.handles = {}
        self.min_width = min_width
        self.min_height = min_height
        self.initSizes()
        self.initContent()
        self.initAssets()
        self.initUI()
        self.initTitle()

    def initUI(self):
        # set flags
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.updateHandles()
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def initContent(self):
        self.content = NodeContentWidget(None)
        self.grContent = QGraphicsProxyWidget(self)
        self.setContentGeometry()
        self.grContent.setWidget(self.content)

    def initAssets(self):
        self._title_color = Qt.white
        self._title_font = QFont('Ubuntu', 8)

        self._color = QColor("#7F00000")
        self._color_selected = QColor("#FFFFA637")
        self._color_hovered = QColor("#FF37A6FF")

        self._pen_default = QPen(self._color)
        self._pen_default.setWidthF(OUTLINE_WIDTH)
        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(OUTLINE_WIDTH)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_hovered.setWidthF(OUTLINE_WIDTH + 1)

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

    def initSizes(self):
        # self.width = 180
        # self.height = 240

        # Diverse parameters for drawing
        self.handleSize = 5
        self.edge_roundness = 15.
        self.edge_padding = 10.
        self.title_height = 24
        self.title_horizontal_padding = 5.
        self.title_vertical_padding = 4.

    def setContentGeometry(self):
        self.content.setGeometry(self.edge_roundness, self.title_height + self.edge_roundness,
                                 self.width - 2 * self.edge_roundness,
                                 self.height - 2 * self.edge_roundness - self.title_height)

    def initTitle(self):
        # Draw the _title
        self._title_color = Qt.white
        self._title_font = QFont('Ubuntu', 10)
        self._padding = 5.
        self.title_height = 24
        self.title_item = QGraphicsTextItem(self)
        # self.title_item.node = self.node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._padding, 0)
        self.title_item.setTextWidth(self.width - 2 * self._padding)
        self.title_item.setPlainText('Resizeable node')

    @property
    def height(self):
        return self.rect().height()

    @property
    def width(self):
        return self.rect().width()

    def updateHandles(self):
        rect = self.boundingRect()
        left, width, top, height = rect.left(), rect.width(), rect.top(), rect.height()
        offset = self.handleSize
        self.handles[Handle.TopLeft] = QRectF(left, top, offset, offset)
        self.handles[Handle.TopMiddle] = QRectF(left + offset, top, width - 2 * offset, offset)
        self.handles[Handle.TopRight] = QRectF(left + width - offset, top, offset, offset)
        self.handles[Handle.BottomLeft] = QRectF(left, top + height - offset, offset, offset)
        self.handles[Handle.MiddleLeft] = QRectF(left, top + offset, offset, height - 2 * offset)
        self.handles[Handle.BottomRight] = QRectF(left + width - offset, top + height - offset, offset, offset)
        self.handles[Handle.MiddleRight] = QRectF(left + width - offset, top + offset, offset, height - 2 * offset)
        self.handles[Handle.BottomMiddle] = QRectF(left + offset, top + height - offset, width - 2 * offset, offset)

    def boundingRect(self):
        # Return rectangle for selection detection
        return self.rect().normalized()

    def handleAt(self, point):
        for handle, rect in self.handles.items():
            if rect.contains(point):
                if DEBUG: print(handle, rect)
                return handle
        else:
            return None

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        # if self.isSelected():
        handle = self.handleAt(event.pos())
        if handle is not None:
            self.setCursor(handleCursors[handle])
        else:
            self.setCursor(Qt.ArrowCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        # if self.isSelected():
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        """
        Executed when the mouse is pressed on the item.
        """
        try:
            self.handleSelected = self.handleAt(event.pos())
            if self.handleSelected:
                # record the position where the mouse was pressed
                self.currentPos = event.pos()
                # current rectangle at mouse pressed
                self.currentRect = self.boundingRect()

            super().mousePressEvent(event)
        except Exception as e:
            print(e)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        """
        Executed when the mouse is released from the item.
        """
        super().mouseReleaseEvent(event)
        self.handleSelected = None
        self.currentPos = None
        self.currentRect = None
        self.update()

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handleSelected is not None:
            self.resize(event.pos())
        else:
            super().mouseMoveEvent(event)

    def resize(self, pos):
        """Update rectangle and bounding rectangle"""
        rect = self.rect()
        boundingRect = self.boundingRect()
        from_left = self.currentRect.left()
        from_right = self.currentRect.right()
        from_top = self.currentRect.top()
        from_bottom = self.currentRect.bottom()
        to_left = from_left + pos.x() - self.currentPos.x()
        to_right = from_right + pos.x() - self.currentPos.x()
        to_top = from_top + pos.y() - self.currentPos.y()
        to_bottom = from_bottom + pos.y() - self.currentPos.y()

        self.prepareGeometryChange()
        update_left, update_top, update_right, update_bottom = handleUpdate[self.handleSelected]
        if update_left:
            if from_right - to_left <= self.min_width:
                boundingRect.setLeft(from_right - self.min_width)
            else:
                boundingRect.setLeft(to_left)
            rect.setLeft(boundingRect.left())
        if update_top:
            if from_bottom - to_top <= self.min_height:
                boundingRect.setTop(from_bottom - self.min_height)
            else:
                boundingRect.setTop(to_top)
            rect.setTop(boundingRect.top())
        if update_bottom:
            if to_bottom - from_top <= self.min_height:
                boundingRect.setBottom(from_top + self.min_height)
            else:
                boundingRect.setBottom(to_bottom)
            rect.setBottom(boundingRect.bottom())
        if update_right:
            if to_right - from_left <= self.min_width:
                boundingRect.setRight(from_left + self.min_width)
            else:
                boundingRect.setRight(to_right)
            rect.setRight(boundingRect.right())

        self.setRect(rect)
        self.updateHandles()
        self.setContentGeometry()

    def shape(self):
        """
        Returns the shape of this item as a QPainterPath in local coordinates.
        """
        path = QPainterPath()
        # path.addRoundedRect(self.rect(), self.edge_size, self.edge_size)
        path.addRect(self.rect())
        return path

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem', widget: Optional[QWidget] = ...) -> None:
        # content
        rect = self.rect()
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(rect, self.edge_roundness, self.edge_roundness)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(rect, self.edge_roundness, self.edge_roundness)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())

        for handle in self.handles.values():

            path_handle = QPainterPath()
            path_handle.addRect(handle)
            painter.drawPath(path_handle)

