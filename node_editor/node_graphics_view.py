from PyQt5.QtWidgets import QGraphicsView, QApplication, QGraphicsProxyWidget
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import enum
from .node_scene import Scene
from .node_edge_dragging import EdgeDragging
from .node_graphics_socket import GraphicsSocket
from .node_graphics_edge import GraphicsEdge
from .node_graphics_cutline import CutLine
from .node_edge_rerouting import EdgeRerouting
from .utils import dumpException
from typing import Callable


class ViewMode(enum.IntEnum):
    """Mode representing when we reroute existing edge ctrl + click"""
    NOOP = 1
    EDGE_DRAG = 2
    EDGE_CUT = 3
    EDGES_REROUTING = 4


EDGE_DRAG_START_THRESHOLD = 50

EDGE_REROUTING_UE = False

DEBUG = False
DEBUG_MRB_SCENE_ITEMS = True
DEBUG_MRB_LAST_SELECTIONS = True


class NodeGraphicsView(QGraphicsView):
    """Implement custom graphics view that holds the scene containing a background and the nodes.
    Holds most key, mouse events."""

    # Register new event scenePosChanged
    # It may be used in node editor window to update the status bar with the mouse position
    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, scene: 'Scene', parent=None):
        """

        Parameters
        ----------
        scene : `Scene`
            reference to the :class:`~nodeeditor.node_scene.Scene`
        parent : ``QWidget``
            parent widget

        Instance Attributes
        -------------------
        - **grScene** - reference to the :class:`~nodeeditor.node_graphics_scene.GraphicsScene`
        - **mode** - state of the `Graphics View`
        - **zoomInFactor**- ``float`` - zoom step scaling, default 1.25
        - **zoomClamp** - ``bool`` - do we clamp zooming or is it infinite?
        - **zoom** - current zoom step
        - **zoomStep** - ``int`` - the relative zoom step when zooming in/out
        - **zoomRange** - ``[min, max]``

        """
        super().__init__(parent=parent)
        self.scene = scene  # reference to parent scene
        self.grScene = scene.grScene  # reference to the graphical implementation of the scene
        self.initUI()  # initialize render settings
        self.setScene(self.grScene)  # set the rendered scene to grScene

        self.mode = ViewMode.NOOP  # Control variable to handle NOOP mode, dragging mode
        self.editingFlag = False  # Control variable set to True when editing the content of a node

        # edge dragging
        self.dragging = EdgeDragging(self)

        # edge rerouting
        self.rerouting = EdgeRerouting(self)

        # cutLine
        self.cutLine = CutLine()
        self.rubberBandDraggingRectangle = False
        self.grScene.addItem(self.cutLine)

        # Zoom parameters
        self.last_scene_mouse_position = QPoint(0, 0)
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 5
        self.zoomStep = 1
        self.zoomRange = [0, 10]

        # listeners for drag and drop event
        self._drag_enter_listeners = []
        self._drop_listeners = []

        # diverses state variables
        self._last_lmb_click_scene_pos = None

    def initUI(self):
        """Define render settings for this `NodeGraphicsView`"""
        # define render settings
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing |
                            QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        # enable drag and drop
        self.setAcceptDrops(True)

    def resetMode(self):
        """Set mode to MODE_NOOP"""
        self.mode = ViewMode.NOOP

    def isInNoOpMode(self):
        """Check if the view is in no operation mode

        Returns
        -------
        ``bool``
            True if in no operation mode
        """
        return self.mode == ViewMode.NOOP

    def isEdgeCutting(self):
        """Check if the view is in edge cutting mode

        Returns
        -------
        ``bool``
            True if in edge cutting mode
        """
        return self.mode == ViewMode.EDGE_CUT

    def isEdgeDragging(self):
        """Check if the view is in edge dragging mode

        Returns
        -------
        ``bool``
            True if in edge dragging mode
        """
        return self.mode == ViewMode.EDGE_DRAG

    def isEdgeRerouting(self):
        """Check if the view is in edge rerouting mode

        Returns
        -------
        ``bool``
            True if in edge rerouting mode
        """
        return self.mode == ViewMode.EDGES_REROUTING

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Trigger our registered `Drag Enter` events"""
        for callback in self._drag_enter_listeners:
            callback(event)

    def dropEvent(self, event: QDropEvent) -> None:
        """Trigger our registered `Drop` events"""
        for callback in self._drop_listeners:
            callback(event)

    def addDragEnterListener(self, callback: Callable):
        """Register callback for `Drag Enter` event

        Parameters
        ----------
        callback : Callable
            callback function
        """
        self._drag_enter_listeners.append(callback)

    def addDropListener(self, callback: Callable):
        """Register callback for `Drop` event

        Parameters
        ----------
        callback : Callable
            callback function
        """
        self._drop_listeners.append(callback)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Redirect click events according to the button pressed"""
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Redirect release events according to the button released"""
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def leftMouseButtonPress(self, event: QMouseEvent):
        """Handle left mouse button click

        Change the current mode depending on which item is clicked on :
            - `Node` or `Edge` + shift : add to selection
            - `Socket` : Edge dragging or rerouting mode
            - `Scene' + ctrl : Edge cutting mode
        Parameters
        ----------
        event : QMouseEvent

        """
        # get the item we clicked on
        item = self.getItemAtClick(event)
        # store the current position of the click for later distance calculation
        self._last_lmb_click_scene_pos = self.mapToScene(event.pos())

        # logic for multiple selection using shift
        self.print('LMB on ', item, self.debug_modifiers(event))
        # TODO Node Content Widget prevent some node selection...
        if hasattr(item, 'node') or isinstance(item, GraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return

        # Click on a socket
        # logic for starting dragging an edge
        if isinstance(item, GraphicsSocket):  # Clicking on a socket
            # Ctrl + click : rerouting mode
            if self.mode == ViewMode.NOOP and event.modifiers() & Qt.ControlModifier:
                socket = item.socket
                if socket.hasAnyEdge():
                    self.mode = ViewMode.EDGES_REROUTING
                    self.rerouting.startRerouting(socket)
                    return  # suppressing other lmb related event

            if self.mode == ViewMode.NOOP:  # when the mode is noop
                self.mode = ViewMode.EDGE_DRAG  # enter dragging mode
                self.dragging.edgeDragStart(item)

                return  # suppressing other lmb related event

        if self.mode == ViewMode.EDGE_DRAG:  # if we already were in edge dragging mode
            res = self.dragging.edgeDragEnd(item)  # check if we click on another valid socket
            if res:
                return  # suppress event if we clicked on a socket

        if item is None:
            # Logic for the cutline (Ctrl + LMB)
            if event.modifiers() & Qt.ControlModifier and self.mode == ViewMode.NOOP:
                self.mode = ViewMode.EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.pos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True

        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):
        """Handle left mouse button is released

        End dragging or rerouting mode
        Parameters
        ----------
        event : QMouseEvent
        """
        # get item which we released mouse button on
        item = self.getItemAtClick(event)
        try:

            self.print('Mouse released at ', item)
            # logic for multiple selection using shift
            if hasattr(item, 'node') or isinstance(item, GraphicsEdge) or item is None:
                if event.modifiers() & Qt.ShiftModifier:
                    event.ignore()
                    fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                            Qt.LeftButton, Qt.NoButton,
                                            event.modifiers() | Qt.ControlModifier)
                    super().mouseReleaseEvent(fakeEvent)
                    return

            # check the distance between the last click and the release
            # if we were basically on the socket we clicked, we keep the edge dragging mode and suppress other events
            # otherwise the edge dragging mode is ended and returned to noop
            if self.mode == ViewMode.EDGE_DRAG:  # if we were dragging an edge
                if self.distanceBetweenClickAndRelease(event):
                    res = self.dragging.edgeDragEnd(item)
                    if res:
                        return  # skip the rest of the code

            if self.mode == ViewMode.EDGES_REROUTING:
                # pass the socket as target if clicked on socket else None
                if not EDGE_REROUTING_UE:
                    # version 2
                    if not self.rerouting.first_mb_release:
                        # for confirmation of first mb release
                        self.rerouting.first_mb_release = True
                        return  # skip the rest of the code
                    self.rerouting.stopRerouting(item.socket if isinstance(item, GraphicsSocket) else None)

                else:
                    self.rerouting.stopRerouting(item.socket if isinstance(item, GraphicsSocket) else None)

                self.mode = ViewMode.NOOP

            # End of cutLine mode
            if self.mode == ViewMode.EDGE_CUT:
                self.cutIntersectingEdges()
                self.cutLine.line_points = []
                self.cutLine.update()
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.mode = ViewMode.NOOP
                return

            # Dragging rectangle selection
            if self.rubberBandDraggingRectangle:
                self.rubberBandDraggingRectangle = False
                current_selected_items = self.grScene.selectedItems()

                if current_selected_items != self.grScene.scene._last_selected_items:
                    if not current_selected_items:
                        self.grScene.itemsDeselected.emit()
                    else:
                        self.grScene.itemSelected.emit()
                    self.grScene.scene._last_selected_items = current_selected_items
                return  # skip the rest of the code

            # otherwise deselect everything
            if item is None:
                self.grScene.itemsDeselected.emit()

        except Exception as e:
            dumpException(e)

        super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event: QMouseEvent):
        """Implement dragging of the scene using middle button"""
        # faking events for enable MMB dragging the scene
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event: QMouseEvent):
        """Implement dragging of the scene using middle button"""
        # when releasing the middle button, release the left button instead and reset the drag mode
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def rightMouseButtonPress(self, event: QMouseEvent):
        """Mostly debug
        """
        item = self.getItemAtClick(event)
        # debug printout
        if DEBUG_MRB_SCENE_ITEMS:
            if isinstance(item, GraphicsEdge):
                self.print("MRB DEBUG:", item.edge, "\n\t", item.edge.grEdge if item.edge.grEdge is not None else None)
                return

            if isinstance(item, GraphicsSocket):
                self.print("MRB DEBUG:", item.socket, "socket_type:", item.socket.socket_type,
                           "input" if item.socket.is_input else "output",
                           "has edges:", "no" if item.socket.edges == [] else "")
                if item.socket.edges:
                    for edge in item.socket.edges:
                        self.print("\t", edge)
                return

            if hasattr(item, 'node'):
                self.print('MRB DEBUG:', item)
                return

            if isinstance(item, QGraphicsProxyWidget):
                self.print('MRB DEBUG', item)
                self.print(item.widget())

            if DEBUG_MRB_SCENE_ITEMS and (item is None or self.mode == ViewMode.EDGES_REROUTING):
                self.print("SCENE:")
                self.print("  Nodes:")
                for node in self.grScene.scene.nodes:
                    self.print("\t", node)
                self.print("  Edges:")
                for edge in self.grScene.scene.edges:
                    self.print("\t", edge, "\n\t\tgrEdge:",
                               edge.grEdge if edge.grEdge is not None else None)
                return

            if event.modifiers() & Qt.CTRL:
                self.print("  Graphic Items in GraphicScene:")
                for item in self.grScene.items():
                    self.print('    ', item)

                return

        if DEBUG_MRB_LAST_SELECTIONS and event.modifiers() & Qt.SHIFT:
            self.print("scene _last_selected_items:", self.grScene.scene._last_selected_items)
            return

        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Overriden Qt's ``mouseMoveEvent`` handling Scene/View logic"""
        scenepos = self.mapToScene(event.pos())

        try:
            if self.mode == ViewMode.EDGE_DRAG:
                self.dragging.updateDestination(scenepos.x(), scenepos.y())

            if self.mode == ViewMode.EDGE_CUT and self.cutLine is not None:
                self.cutLine.line_points.append(scenepos)
                self.cutLine.update()

            if self.mode == ViewMode.EDGES_REROUTING:
                self.rerouting.updateScenePos(scenepos.x(), scenepos.y())
        except Exception as e:
            dumpException(e)

        self.last_scene_mouse_position = scenepos

        # Trigger new event scenePosChanged returning the current mouse position
        self.scenePosChanged.emit(int(scenepos.x()), int(scenepos.y()))

        super().mouseMoveEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # if event.key() == Qt.Key_Delete:
        #     if not self.editingFlag:
        #         self.deleteSelected()
        #     else:
        #         super().keyPressEvent(event)
        # elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.saveToFile('graph.json')
        #
        # elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.loadFromFile('graph.json')
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and not event.modifiers() & Qt.ShiftModifier:
        #     self.grScene.scene.history.undo()
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
        #     self.grScene.scene.history.redo()
        # elif event.key() == Qt.Key_H:
        #     if DEBUG:
        #         print('History : {}'.format(len(self.scene.history.history_stack)))
        #         print(' -- Current step', self.scene.history.history_current_step)
        #         for ix, item in enumerate(self.grScene.scene.history.history_stack):
        #             print(ix, ' - ', item['desc'])
        #
        # else:

        super().keyPressEvent(event)

    def cutIntersectingEdges(self):
        """Compare which `Edges` intersect with current `Cut line` and delete them safely"""
        for ix in range(len(self.cutLine.line_points) - 1):
            p1 = self.cutLine.line_points[ix]
            p2 = self.cutLine.line_points[ix + 1]

            for edge in self.grScene.scene.edges:
                if edge.grEdge.intersectsWith(p1, p2):
                    edge.remove()

        self.grScene.scene.history.storeHistory('Delete cutted edges')

    def deleteSelected(self):
        """Shortcut for safe deleting every object selected in the `Scene`."""
        for item in self.grScene.selectedItems():
            if isinstance(item, GraphicsEdge):
                self.print('deleteSelected - removing edge ', item)
                item.edge.remove()

            elif hasattr(item, 'node'):
                self.print('deleteSelected - removing node ', item)
                item.node.remove()
        self.grScene.scene.history.storeHistory('Delete selected', setModified=True)

    def debug_modifiers(self, event):
        out = 'MODS: '
        if event.modifiers() & Qt.ShiftModifier: out += 'SHIFT'
        if event.modifiers() & Qt.ControlModifier: out += 'CTRL'
        if event.modifiers() & Qt.AltModifier: out += 'ALT'
        return out

    def wheelEvent(self, event: QWheelEvent) -> None:
        """overridden Qt's ``wheelEvent``. This handles zooming"""
        # TODO fix wheelevent when the node implement wheel event ?
        try:
            item = self.getItemAtClick(event)
            self.print(item)
        except Exception as e:
            dumpException(e)

        # calculate zoom factor
        zoomOutFactor = 1 / self.zoomInFactor

        # calculate zoom
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        # clamp the zoom to [zooRange]
        clamped = False
        if self.zoom < self.zoomRange[0]:
            self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]:
            self.zoom, clamped = self.zoomRange[1], True
        # set scene scale
        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)  # call to native graphics view scale

        # zoom centered on the mouse
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def getItemAtClick(self, event: QEvent):
        """Return the object on which we've clicked/release mouse button

        Parameters
        ----------
        event: ``QEvent``
            Qt's mouse or key event

        Returns
        -------
            ``QGraphicsItem`` which the mouse event happened or ``None``
        """
        # TODO merge with getItemAt from node_scene ?
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def distanceBetweenClickAndRelease(self, event: QMouseEvent):
        """Measures if we are too far from the last LMB click scene position.
        This is used for detection if we release too far after we clicked on a `Socket`

        Parameters
        ----------
        event : `QMouseEvent`

        Returns
        -------
        ``bool``
            ``True`` if we released too far from where we clicked before

        """
        new_lmb_click_scene_pos = self.mapToScene(event.pos())
        dist_scene_pos = new_lmb_click_scene_pos - self._last_lmb_click_scene_pos
        return dist_scene_pos.x() ** 2 + dist_scene_pos.y() ** 2 >= EDGE_DRAG_START_THRESHOLD ** 2

    def print(self, *args):
        if DEBUG:
            print('>NodeGraphicsView : ', *args)
