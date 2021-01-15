from PyQt5.QtWidgets import QGraphicsItem, QGraphicsProxyWidget, QGraphicsTextItem, QWidget, \
    QGraphicsRectItem, QStyleOptionGraphicsItem, QGraphicsSceneMouseEvent, QGraphicsDropShadowEffect
from PyQt5.QtGui import QFont, QPen, QColor, QBrush, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QRectF, QPointF
from .utils import dumpException, print_func_name
from .node_handle import HandlePosition, Handle
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .node_node import Node

OUTLINE_WIDTH = 1.0
DEBUG = True
DEBUG_HANDLE = True


# TODO Review the init arguments

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
            self.initHandles()

        # init _title
        self.title_item = None
        self.initTitle()
        self.title = self.node.title
        # init content
        self.initContent()
        self.updateLayout()

    def initSizes(self):
        # Diverse parameters for drawing
        self.edge_roundness = 15.
        self.edge_padding = 10.
        self.title_height = 24
        self.title_horizontal_padding = 5.
        self.title_vertical_padding = 4.

        # TODO min and size at the same place
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

    def initHandles(self):
        for position in (HandlePosition.MiddleRight, HandlePosition.BottomMiddle, HandlePosition.BottomRight):
            self.handles[position] = Handle(self, position)

    def initContent(self):
        """Add the `Content` of the `Node` to the `Graphical Scene`
        """
        # Draw the contents
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

    def setContentGeometry(self):
        """Set Content geometry to fit the space available in the `Graphical Node`
        """
        if self.title_item:
            self.title_item.setTextWidth(self.width - 2 * self.title_horizontal_padding)
        if self.content is not None:
            self.content.setGeometry(self.edge_padding, self.title_height + self.edge_padding,
                                     self.width - 2 * self.edge_padding,
                                     self.height - 2 * self.edge_padding - self.title_height)

    def doSelect(self, new_state=True):
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state:
            self.onSelected()

    def onSelected(self):
        """onSelected event"""
        # TODO insert callback ?
        self.print('On selected event', self.node)
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
        # When the node move because of drag
        # update the corresponding edges0

        # self.node.updateConnectedEdges()  # only work in the case one node is selected
        # TODO trigger event when resizing
        # if self.resizeable and self.handleSelected is not None:
        #     self.resize(event.pos())
        #     return
        # else:
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

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def resize(self, rect: QRectF):
        """Update rectangle and bounding rectangle"""
        if rect.width() < self.min_width:
            rect.setWidth(self.min_width)
        if rect.height() < self.min_height:
            rect.setHeight(self.min_height)
        self.setRect(rect)
        self.updateSocketAndEdges()
        self.setContentGeometry()

    def updateSocketAndEdges(self):
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
        try:
            # TO implement
            # rect = self.rect()
            # x, y = rect.left(), rect.top()
            x = y = 0
            # shadow_path = QPainterPath()
            # shadow_path.setFillRule(Qt.WindingFill)
            # offset = 3
            # shadow_path.addRoundedRect(x + offset, y + offset, self.width + offset, self.height + offset,
            #                            self.edge_roundness, self.edge_roundness)
            # painter.setPen(Qt.NoPen)
            # painter.setBrush(self._brush_title)
            # painter.drawPath(shadow_path.simplified())

            path_title = QPainterPath()
            path_title.setFillRule(Qt.WindingFill)
            # Rectangle for title
            path_title.addRoundedRect(x, y, self.width, self.title_height, self.edge_roundness, self.edge_roundness)
            path_title.addRect(x, y + self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
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
            path_outline.addRoundedRect(x - 1, y - 1,
                                        self.width + 2, self.height + 2,
                                        self.edge_roundness, self.edge_roundness)
            painter.setBrush(Qt.NoBrush)
            if self.hovered:
                painter.setPen(self._pen_hovered)
                painter.drawPath(path_outline.simplified())
                painter.setPen(self._pen_default)
                painter.drawPath(path_outline.simplified())
            else:
                painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
                painter.drawPath(path_outline.simplified())
        except Exception as e:
            dumpException(e)
