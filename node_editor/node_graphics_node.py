from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QWidget, \
    QGraphicsRectItem, QStyleOptionGraphicsItem, QGraphicsSceneMouseEvent, QGraphicsDropShadowEffect, \
    QGraphicsSceneWheelEvent, QGraphicsSceneHoverEvent
from PyQt5.QtGui import QFont, QPen, QColor, QBrush, QPainter, QPainterPath, QImage, QFontMetrics
from PyQt5.QtCore import Qt, QRectF
from .node_handle import HandlePosition, Handle
from .node_socket import SocketPosition
from .utils import dumpException

from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from .node_node import Node

OUTLINE_WIDTH = 2.0
DEBUG = False

THEME = 'LIGHT'

colors = {'DARK': {
    'title_color': Qt.white,
    'color': QColor("#7F00000"),
    'color_selected': QColor("#FFFFA637"),
    'color_hovered': QColor("#FF37A6FF"),
    'brush_title': QBrush(QColor("#FF313131")),
    'brush_background': QBrush(QColor("#E3212121"))
},
    'LIGHT': {
        'title_color': Qt.black,
        'color': QColor("#7Ff0f0f0"),
        'color_selected': QColor("#FFFFA637"),
        'color_hovered': QColor("#FF06acee"),
        'brush_title': QBrush(QColor("#FFFFFFFF")),
        'brush_background': QBrush(QColor("#fff0f0f0")),
    }
}


class GraphicsNode(QGraphicsRectItem):
    """Implement the graphics version of a node"""

    def __init__(self, node: 'Node', parent=None, resizeable=True, min_width=180, width=180, min_height=240,
                 height=240):
        super().__init__(parent=parent)
        self.node = node  # Reference to parent class Node implementing the logic
        # init flags
        self._was_moved = False
        self._resized = False
        self._last_selected_state = False
        self._hovered = False

        try:
            self.handles = {}
            self._currentRect = None
            self._currentPos = None

            self.initSizes(resizeable=resizeable, min_width=min_width, width=width, min_height=min_height,
                           height=height)
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
        # fm = QFontMetrics(self._title_font)
        # width = fm.width(self.node.title)
        self.title_item.setPlainText(self._title)
        # self.title_item.setTextWidth(width)

    def initUI(self):
        # Define the node as selectable and movable
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)
        if self.resizeable:
            self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
            self.setFlag(QGraphicsItem.ItemIsFocusable, True)
            self.initHandles()

        # init _title
        self.title_item = None
        self.initTitle()
        self.title = self.node.title
        # init content
        self.initContent()
        self.updateLayout()

    def initSizes(self, resizeable=True, min_width=180, width=180, min_height=240, height=240):
        # Diverse parameters for drawing
        self.edge_roundness = 15.
        self.edge_padding = 10.
        self.title_height = 24
        self.title_horizontal_padding = 5.
        self.title_vertical_padding = 4.

        self.content_offset = 2  # define margin for the content

        self.resizeable = resizeable
        self.min_width = min_width
        self.min_height = min_height
        self.width = width
        self.height = height

        # Socket parameters
        self.socket_spacing = 22
        self.socket_offsets = {
            SocketPosition.BottomLeft: -1,
            SocketPosition.MiddleLeft: -1,
            SocketPosition.TopLeft: -1,
            SocketPosition.BottomRight: 1,
            SocketPosition.MiddleRight: 1,
            SocketPosition.TopRight: 1,
        }

    def initAssets(self):
        self._title_color = colors[THEME]['title_color']
        self._title_font = QFont('Ubuntu', 8)

        self._color = colors[THEME]['color']
        self._color_selected = colors[THEME]['color_selected']
        self._color_hovered = colors[THEME]['color_hovered']

        self._pen_default = QPen(self._color)
        self._pen_default.setWidthF(OUTLINE_WIDTH)
        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(OUTLINE_WIDTH)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_hovered.setWidthF(OUTLINE_WIDTH + 1)

        self._brush_title = colors[THEME]['brush_title']
        self._brush_background = colors[THEME]['brush_background']

        self.icons = QImage('../../node_editor/icons/status_icons.png')

        shadow = QGraphicsDropShadowEffect(blurRadius=5, xOffset=3, yOffset=3)
        self.setGraphicsEffect(shadow)

    def initHandles(self):
        for position in (HandlePosition.MiddleRight, HandlePosition.BottomMiddle, HandlePosition.BottomRight):
            self.handles[position] = Handle(self, position)

    def initContent(self):
        """Add the `Content` of the `Node` to the `Graphical Scene`"""
        # Draw the contents
        # defines the content as a proxy widget with parent self
        if self.content:
            self.grContent = self.node.scene.grScene.addWidget(self.content)
            self.grContent.setParentItem(self)

    def initTitle(self):
        """Title is instanciated as `QGraphicsTextItem`"""
        # Draw the _title
        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = self.node  # add reference to the node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.title_horizontal_padding, 0)

    def setContentGeometry(self, ):
        """Set Content geometry to fit the space available in the `Graphical Node`"""
        if self.title_item:
            self.title_item.setTextWidth(self.width - 2 * self.title_horizontal_padding)
        offset = self.content_offset
        if self.content is not None:
            self.content.setGeometry(self.edge_padding + offset,
                                     self.title_height + self.edge_padding + offset,
                                     self.width - 2 * self.edge_padding - 2 * offset,
                                     self.height - 2 * self.edge_padding - self.title_height - 2 * offset)

    def enableHoverEvents(self, enabled: bool = True):
        self.setAcceptHoverEvents(enabled)
        if not enabled:
            self._hovered = False

    def doSelect(self, new_state=True):
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state:
            self.onSelected()

    def onSelected(self):
        """onSelected event"""
        self.print('On selected event', self.node)
        self.node.scene.grScene.itemSelected.emit()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        """Overrides Qt's mousePressEvent.
        Parameters
        ----------
        event : QGraphicsSceneMouseEvent
            current event
        """
        try:
            # self.handleSelected = self.getHandleAt(event.pos())
            # if self.handleSelected:
            #     # record the position where the mouse was pressed
            #     self._currentPos = event.pos()
            #     # # current rectangle at mouse pressed
            #     self._currentRect = self.boundingRect()
            super().mousePressEvent(event)
        except Exception as e:
            dumpException(e)

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
        self.updateSocketAndEdges()
        self._was_moved = True
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'):
        """Mouse Release Event

        On release, if moved, trigger storeHistory from :class:`~node_editor.node_scene_history.SceneHistory`.
        Also handles selection of the node and triggers onSelected event.
        Parameters
        ----------
        event : QGraphicsSceneMouseEvent
            event triggering the mouseReleaseEvent
        """
        # TODO onDeselected
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

    def wheelEvent(self, event: 'QGraphicsSceneWheelEvent') -> None:
        """wheelEvent on the GraphicsNode. Avoid the wheelEvent from the GraphicsScene."""
        self.print('wheelEvent')

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        super().hoverEnterEvent(event)
        self._hovered = True
        self.update()

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        super().hoverLeaveEvent(event)
        self._hovered = False
        self.update()

    def resize(self, rect: QRectF):
        """Update rectangle and bounding rectangle"""
        if rect.width() < self.min_width:
            rect.setWidth(self.min_width)
        if rect.height() < self.min_height:
            rect.setHeight(self.min_height)
        self.setRect(rect)
        self.updateSocketAndEdges()
        self.setContentGeometry()

    def getSocketPosition(self, index: int, position: SocketPosition, num_out_of: int = 1) -> List[float]:
        """Helper function - returns the position of a socket in pixels relative to the `Graphical Node`

        Parameters
        ----------
        index : ```int```
            Index of the socket in the list
        position : SocketPosition
            One of enumeration
        num_out_of : ```int```
            total number of `Socket` on this position

        Returns
        -------
        ```list```
            x, y position relative to the node
        """
        if position in (SocketPosition.TopLeft, SocketPosition.MiddleLeft, SocketPosition.BottomLeft):
            x = self.socket_offsets[position]
        else:
            x = self.width + self.socket_offsets[position]

        if position in (SocketPosition.BottomLeft, SocketPosition.BottomRight):
            # start from bottom
            y = self.height - (index * self.socket_spacing + self.grNode.title_vertical_padding + self.edge_roundness)

        elif position in (SocketPosition.MiddleLeft, SocketPosition.MiddleRight):
            num_sockets = num_out_of
            node_height = self.height
            top_offset = self.title_height + 2 * self.title_vertical_padding + self.edge_padding
            available_height = node_height - top_offset

            total_height_of_all_socket = num_sockets * self.socket_spacing

            new_top = available_height - total_height_of_all_socket

            # y = top_offset + index * self.socket_spacing + new_top / 2
            y = top_offset + available_height / 2. + (index - 0.5) * self.socket_spacing - \
                (num_sockets - 1) * self.socket_spacing / 2

        elif position in (SocketPosition.TopLeft, SocketPosition.TopRight):
            # start from top
            y = index * self.socket_spacing + self.title_height + self.title_vertical_padding + self.edge_roundness
        else:
            y = 0

        return [x, y]

    def updateSocketAndEdges(self):
        """Update the `Socket` position and the `Graphical Edges` when available"""
        # As this method can
        if self.resizeable:
            # update the socket position
            if hasattr(self.node, 'inputs') and hasattr(self.node, 'outputs'):
                for socket in self.node.getSockets():
                    socket.setSocketPosition()

        # in any case
        if self.scene() is not None:
            for node in self.scene().scene.nodes:
                if node.isSelected():
                    node.updateConnectedEdges()

    def updateHandles(self):
        for handle in self.handles.values():
            handle.setHandlePosition()

    def updateLayout(self):
        """Updates the layout.

        Updates :
        - Socket position
        - Edges connected to the node
        - Position of the handle to resize
        - Size of the content
        """
        self.updateSocketAndEdges()
        self.updateHandles()
        self.setContentGeometry()

    def print(self, *args):
        if DEBUG:
            print('>GraphicsNode : ', *args)

    def boundingRect(self):
        # Return rectangle for selection detection
        rect = self.rect()
        x, y = rect.left(), rect.top()
        return QRectF(x, y, self.width, self.height)

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem',
              widget: Optional[QWidget] = ...) -> None:
        x = y = 0

        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)

        # Rectangle for title
        path_title.addRoundedRect(x, y, self.width, self.title_height,
                                  self.edge_roundness, self.edge_roundness)
        path_title.addRect(x, y + self.title_height - self.edge_roundness,
                           self.edge_roundness, self.edge_roundness)
        path_title.addRect(x + self.width - self.edge_roundness, y + self.title_height - self.edge_roundness,
                           self.edge_roundness, self.edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(x, y + self.title_height,
                                    self.width, self.height - self.title_height,
                                    self.edge_roundness, self.edge_roundness)
        path_content.addRect(x, y + self.title_height,
                             self.edge_roundness, self.edge_roundness)
        path_content.addRect(x + self.width - self.edge_roundness, y + self.title_height,
                             self.edge_roundness, self.edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(x, y, self.width, self.height,
                                    self.edge_roundness, self.edge_roundness)
        painter.setBrush(Qt.NoBrush)
        if self._hovered:
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
            painter.drawPath(path_outline.simplified())

        # status
        # offset = 24.0
        # if self.node.isDirty(): offset = 0.
        # if self.node.isInvalid(): offset = 48.
        # painter.drawImage(QRectF(-10., -10., 24., 24.),
        #                   self.icons,
        #                   QRectF(offset, 0, 24., 24.))
