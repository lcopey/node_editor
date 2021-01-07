from PyQt5.QtWidgets import QGraphicsItem, QGraphicsProxyWidget, QGraphicsTextItem, QWidget, \
    QGraphicsRectItem, QStyleOptionGraphicsItem, QGraphicsSceneMouseEvent
from PyQt5.QtGui import QFont, QPen, QColor, QBrush, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QRectF, QPointF
from .utils import dumpException, print_func_name
from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .node_node import Node

OUTLINE_WIDTH = 1.0
DEBUG = False
DEBUG_HANDLE = False


class Handle(Enum):
    # TopLeft = 1
    # TopMiddle = 2
    # TopRight = 3
    # MiddleLeft = 4
    MiddleRight = 5
    # BottomLeft = 6
    BottomMiddle = 7
    BottomRight = 8


handleCursors = {
    # Handle.TopLeft: Qt.SizeFDiagCursor,
    # Handle.TopMiddle: Qt.SizeVerCursor,
    # Handle.TopRight: Qt.SizeBDiagCursor,
    # Handle.MiddleLeft: Qt.SizeHorCursor,
    Handle.MiddleRight: Qt.SizeHorCursor,
    # Handle.BottomLeft: Qt.SizeBDiagCursor,
    Handle.BottomMiddle: Qt.SizeVerCursor,
    Handle.BottomRight: Qt.SizeFDiagCursor,
}

handleUpdate = {
    # Handle.TopLeft: (True, True, False, False),
    # Handle.TopMiddle: (False, True, False, False),
    # Handle.TopRight: (False, True, True, False),
    # Handle.MiddleLeft: (True, False, False, False),
    Handle.MiddleRight: (False, False, True, False),
    # Handle.BottomLeft: (True, False, False, True),
    Handle.BottomMiddle: (False, False, False, True),
    Handle.BottomRight: (False, False, True, True),
}


class GraphicsNode(QGraphicsRectItem):
    """Implement the graphics version of a node"""

    def __init__(self, node: 'Node', parent=None, resizeable=True, min_height=240, min_width=180):
        super().__init__(parent=parent)
        self.node = node  # Reference to parent class Node implementing the logic
        # init flags
        self._was_moved = False
        self._resized = False
        self._last_selected_state = False
        self.hovered = False
        self.resizeable = resizeable
        # init attributes
        self.min_height = min_height
        self.min_width = min_width

        try:
            self.handleSelected = None
            self.handles = {}
            self._currentRect = None
            self._currentPos = None

            self.initSizes()
            self.initAssets()
            self.initUI()

        except Exception as e:
            dumpException(e)

    @property
    def content(self):
        """Reference to the `Node` Content"""
        return self.node.content if self.node else None

    @property
    def height(self):
        return self.rect().height()

    @property
    def width(self):
        return self.rect().width()

    @height.setter
    def height(self, value):
        currentRect = self.rect()
        currentRect.setHeight(value)
        self.setRect(currentRect)

    @width.setter
    def width(self, value):
        currentRect = self.rect()
        currentRect.setWidth(value)
        self.setRect(currentRect)

    @property
    def title(self, ):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    def initUI(self):
        # Define the node as selectable and movable
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)
        if self.resizeable:
            self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
            self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        # self.updateHandles()

        # init _title
        self.initTitle()
        self.title = self.node.title
        # init content
        self.initContent()
        self.updateLayout()

    def initSizes(self):
        self.handleSize = 8
        # Diverse parameters for drawing
        self.edge_roundness = 15.
        self.edge_padding = 10.
        self.title_height = 24
        self.title_horizontal_padding = 5.
        self.title_vertical_padding = 4.

        self.width = 180
        self.height = 240

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

    def initContent(self):
        """Add the `Content` of the `Node` to the `Graphical Scene`
        """
        # Draw the contents
        # if self.content is not None:
        #     self.setContentGeometry()

        # self.grContent = QGraphicsProxyWidget(self)  # defines the content as a proxy widget with parent self
        self.grContent = self.node.scene.grScene.addWidget(self.content)
        self.grContent.setParentItem(self)

    def initTitle(self):
        """Title is instanciated as `QGraphicsTextItem`

        Returns
        -------

        """
        # Draw the _title
        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = self.node  # add reference to the node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.title_horizontal_padding, 0)
        # TODO update with resize ?
        self.title_item.setTextWidth(self.width - 2 * self.title_horizontal_padding)

    def setContentGeometry(self):
        """Set Content geometry to fit the space available in the `Graphical Node`
        """
        self.content.setGeometry(self.edge_padding, self.title_height + self.edge_padding,
                                 self.width - 2 * self.edge_padding,
                                 self.height - 2 * self.edge_padding - self.title_height)

    def updateHandles(self):
        """Update the position of the handles outlying the node.

        This method should be called when resizing the node
        """
        rect = self.boundingRect()
        left, width, top, height = rect.left(), rect.width(), rect.top(), rect.height()

        offset = self.handleSize
        # self.handles[Handle.TopLeft] = QRectF(left, top, offset, offset)
        # self.handles[Handle.TopMiddle] = QRectF(left + offset, top, width - 2 * offset, offset)
        # self.handles[Handle.TopRight] = QRectF(left + width - offset, top, offset, offset)
        # self.handles[Handle.BottomLeft] = QRectF(left, top + height - offset, offset, offset)
        # self.handles[Handle.MiddleLeft] = QRectF(left, top + offset, offset, height - 2 * offset)
        self.handles[Handle.BottomRight] = QRectF(left + width - offset, top + height - offset, offset, offset)
        self.handles[Handle.MiddleRight] = QRectF(left + width - offset, top + offset, offset, height - 2 * offset)
        self.handles[Handle.BottomMiddle] = QRectF(left + offset, top + height - offset, width - 2 * offset, offset)

    def getHandleAt(self, point: QPointF):
        """

        Parameters
        ----------
        point : QPointF
            Position to test

        Returns
        -------
        Handle
            `Handle` beneath to point

        """
        for handle, rect in self.handles.items():
            if rect.contains(point):
                if DEBUG: print(handle, rect)
                return handle
        else:
            return None

    def doSelect(self, new_state=True):
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state:
            self.onSelected()

    def onSelected(self):
        self.node.scene.grScene.itemSelected.emit()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        """When clicking on the node


        When the mouse is pressed on the `Graphical Node`, stores the current position and retangle
        to prepare for resizing event.
        Parameters
        ----------
        event : QGraphicsSceneMouseEvent
            current event
        """
        try:
            self.handleSelected = self.getHandleAt(event.pos())
            if self.handleSelected:
                # record the position where the mouse was pressed
                self._currentPos = event.pos()
                # # current rectangle at mouse pressed
                self._currentRect = self.boundingRect()

            super().mousePressEvent(event)
        except Exception as e:
            print(e)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        """Mouse move event

        Handle two cases :
            - either the `Graphical Node` is resizeable and a handle is selected, the trigger the resize event
            - or the node is selected and update the `Graphical Socket` and `Graphical Edge`.
        Parameters
        ----------
        event : QGraphicsSceneMouseEvent
            event trigerring the mouseMoveEvent
        """
        # When the node move because of drag
        # update the corresponding edges0

        # self.node.updateConnectedEdges()  # only work in the case one node is selected
        # TODO trigger event when resizing
        if self.resizeable and self.handleSelected is not None:
            self.resize(event.pos())
            return
        else:
            self.updateConnected()
            self._was_moved = True
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'):
        """Mouse Release Event

        On release, if moved, trigger storeHistory from :class:`~node_editor.node_scene_history.SceneHistory`.
        Parameters
        ----------
        event : QGraphicsSceneMouseEvent
            event triggering the mouseReleaseEvent
        """
        super().mouseReleaseEvent(event)

        if self.resizeable:
            self.handleSelected = None
            self._currentRect = None
            self._currentPos = None

        # handle when grNode moved
        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.storeHistory('Node moved', setModified=True)

            self.node.scene.resetLastSelectedStates()
            self.doSelect()
            # store the last selected state, because moving also select the node
            self.node.scene._last_selected_items = self.node.scene.getSelectedItems()

            # skip storing selection
            return

        # handle when grNode was clicked on
        # condition met when changing from one selection to another or
        # when multiple items are selected and the current node is then selected
        if self._last_selected_state != self.isSelected() or \
                self.node.scene._last_selected_items != self.node.scene.getSelectedItems():
            # reset all other selected flags to False
            self.node.scene.resetLastSelectedStates()
            # set the new state of this object only
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        """Overrides double click event. Resent to `Node::onDoubleClicked`"""
        self.node.onDoubleClicked(event)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = True
        self.update()

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        # if self.isSelected():
        if self.resizeable:
            handle = self.getHandleAt(event.pos())
            if handle is not None:
                self.setCursor(handleCursors[handle])
            else:
                self.setCursor(Qt.ArrowCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = False
        if self.resizeable:
            self.setCursor(Qt.ArrowCursor)
        self.update()
        super().hoverLeaveEvent(event)

    def resize(self, pos):
        """Update rectangle and bounding rectangle"""
        rect = self.rect()
        boundingRect = self.boundingRect()
        from_left = self._currentRect.left()
        from_right = self._currentRect.right()
        from_top = self._currentRect.top()
        from_bottom = self._currentRect.bottom()
        to_left = from_left + pos.x() - self._currentPos.x()
        to_right = from_right + pos.x() - self._currentPos.x()
        to_top = from_top + pos.y() - self._currentPos.y()
        to_bottom = from_bottom + pos.y() - self._currentPos.y()

        if to_left != 0 or to_right != 0 or to_top != 0 or to_bottom != 0:
            self._resized = True
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
            self.updateLayout()
            # self.updateConnected()
            # self.updateHandles()
            # self.setContentGeometry()
            self.update()

    def updateConnected(self):
        """Update the `Socket` position and the `Graphical Edges` when available"""
        # As this method can
        if self.resizeable:
            # update the socket position
            if hasattr(self.node, 'inputs') and hasattr(self.node, 'outputs'):
                for socket in self.node.inputs + self.node.outputs:
                    socket.setSocketPosition()

        # in any case
        if self.scene() is not None:
            for node in self.scene().scene.nodes:
                if node.isSelected():
                    node.updateConnectedEdges()

    def updateLayout(self):
        """Updates the layout.

        Updates :
        - Socket position
        - Edges connected to the node
        - Position of the handle to resize
        - Size of the content
        """
        self.updateConnected()
        self.updateHandles()
        self.setContentGeometry()

    def boundingRect(self):
        # Return rectangle for selection detection
        return QRectF(0, 0, self.width, self.height). \
            adjusted(-self.handleSize // 2, -self.handleSize // 2, self.handleSize // 2, self.handleSize // 2)
        # return self.rect().adjusted(-self.handleSize // 2, -self.handleSize // 2, self.handleSize // 2,
        #                             self.handleSize // 2)

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem',
              widget: Optional[QWidget] = ...) -> None:
        # _title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, self.edge_roundness, self.edge_roundness)
        path_title.addRect(0, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        path_title.addRect(self.width - self.edge_roundness, self.title_height - self.edge_roundness,
                           self.edge_roundness,
                           self.edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height,
                                    self.edge_roundness,
                                    self.edge_roundness)
        path_content.addRect(0, self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(self.width - self.edge_roundness, self.title_height, self.edge_roundness,
                             self.edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(-1, -1, self.width + 2, self.height + 2, self.edge_roundness, self.edge_roundness)
        painter.setBrush(Qt.NoBrush)
        if self.hovered:
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
            painter.drawPath(path_outline.simplified())

        if DEBUG_HANDLE:
            for handle in self.handles.values():
                try:
                    path_handle = QPainterPath()
                    path_handle.addRect(handle)
                    painter.drawPath(path_handle)
                except Exception as e:
                    dumpException(e)
