from PyQt5.QtWidgets import QGraphicsView, QApplication
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .node_scene import Scene
from .node_edge import Edge, EDGE_TYPE_BEZIER
from .node_graphics_socket import QNEGraphicsSocket
from .node_graphics_edge import QNEGraphicsEdge
from .node_graphics_cutline import QNECutLine

MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_EDGE_CUT = 3

EDGE_DRAG_START_THRESHOLD = 10

from debug.debug import print_func_name, print_scene, print_items

DEBUG = True


class QNEGraphicsView(QGraphicsView):
    """Implement custom graphics view that holds the scene containing a background and the nodes.

    The logic and mouse events are implemented here"""

    # Register new event scenePosChanged
    # It may be used in node editor window to update the status bar with the mouse position
    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, scene: 'Scene', parent=None):
        super().__init__(parent=parent)
        self.scene = scene  # reference to parent scene
        self.grScene = scene.grScene  # reference to the graphical implementation of the scene
        self.initUI()  # initialize render settings
        self.setScene(self.grScene)  # set the rendered scene to grScene

        self.mode = MODE_NOOP  # Control variable to handle NOOP mode, dragging mode
        self.editingFlag = False  # Control variable set to True when editing the content of a node

        # Zoom parameters
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 5
        self.zoomStep = 1
        self.zoomRange = [0, 10]

        # cutLine
        self.cutLine = QNECutLine()
        self.rubberBandDraggingRectangle = False
        self.grScene.addItem(self.cutLine)

    def initUI(self):
        """Define render settings"""
        # define render settings
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | \
                            QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        # self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

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

    def middleMouseButtonPress(self, event: QMouseEvent):
        """Implement dragging of the scene using middle button"""
        # release event from left click ?
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        # change to drag mode, only work when left button click is used
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        # simulate as if the left button was pressed
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.button() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event: QMouseEvent):
        """Implement dragging of the scene using middle button"""
        # when releasing the middle button, release the left button instead and reset the drag mode
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def leftMouseButtonPress(self, event):
        # get the item we clicked on
        item = self.getItemAtClick(event)
        # store the current position of the click for later distance calculation
        self.last_lmb_click_scene_pos = self.mapToScene(event.pos())

        # logic for multiple selection using shift
        if DEBUG: print('LMB on ', item, self.debug_modifiers(event))

        if hasattr(item, 'node') or isinstance(item, QNEGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return

        # logic for starting dragging an edge
        if type(item) == QNEGraphicsSocket:  # Clicking on a socket
            if self.mode == MODE_NOOP:  # when the mode is noop
                self.mode = MODE_EDGE_DRAG  # enter dragging mode
                self.edgeDragStart(item)

                return  # suppressing other lmb related event

        if self.mode == MODE_EDGE_DRAG:  # if we already were in edge dragging mode
            res = self.edgeDragEnd(item)  # check if we click on another valid socket
            if res: return  # suppress event if we clicked on a socket

        if item is None:
            # Logic for the cutline (Ctrl + LMB)
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.pos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True

        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):

        # get item which we released mouse button on
        item = self.getItemAtClick(event)

        if DEBUG: print('Mouse released at ', item)
        # logic for multiple selection using shift
        if hasattr(item, 'node') or isinstance(item, QNEGraphicsEdge) or item is None:
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
        if self.mode == MODE_EDGE_DRAG:  # if we were dragging an edge
            if self.distanceBetweenClickAndRelease(event):
                res = self.edgeDragEnd(item)
                if res: return

        # End of cutLine mode
        if self.mode == MODE_EDGE_CUT:
            self.cutIntersectingEdges()
            self.cutLine.line_points = []
            self.cutLine.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mode = MODE_NOOP
            return

        if self.rubberBandDraggingRectangle:
            # TODO Do not store if selection stay the same
            self.scene.history.storeHistory('Selection changed')
            self.rubberBandDraggingRectangle = False

        super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

        item = self.getItemAtClick(event)
        if DEBUG:
            if item is None:
                print_scene(self.scene)
            else:
                print_items(item)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.dragEdge.grEdge.setDestination(pos.x(), pos.y())
            self.dragEdge.grEdge.update()

        if self.mode == MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutLine.line_points.append(pos)
            self.cutLine.update()

        self.last_scene_mouse_position = self.mapToScene(event.pos())

        # Trigger new event scenePosChanged returning the current mouse position
        self.scenePosChanged.emit(
            int(self.last_scene_mouse_position.x()),
            int(self.last_scene_mouse_position.y())
        )

        super().mouseMoveEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # if event.key() == Qt.Key_Delete:
        #     if not self.editingFlag:
        #         self.deleteSelected()
        #     else:
        #         super().keyPressEvent(event)
        # elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.saveToFile('graph.json.txt')
        #
        # elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.loadFromFile('graph.json.txt')
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
        for ix in range(len(self.cutLine.line_points) - 1):
            p1 = self.cutLine.line_points[ix]
            p2 = self.cutLine.line_points[ix + 1]

            for edge in self.grScene.scene.edges:
                if edge.grEdge.intersectsWith(p1, p2):
                    edge.remove()

        self.grScene.scene.history.storeHistory('Delete cutted edges')

    def deleteSelected(self):
        for item in self.grScene.selectedItems():
            if isinstance(item, QNEGraphicsEdge):
                item.edge.remove()

            elif hasattr(item, 'node'):
                item.node.remove()
        self.grScene.scene.history.storeHistory('Delete selected', setModified=True)

    def debug_modifiers(self, event):
        out = 'MODS: '
        if event.modifiers() & Qt.ShiftModifier: out += 'SHIFT'
        if event.modifiers() & Qt.ControlModifier: out += 'CTRL'
        if event.modifiers() & Qt.AltModifier: out += 'ALT'
        return out

    def wheelEvent(self, event: QWheelEvent) -> None:
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

    def getItemAtClick(self, event):
        """Return the object on which we clicked"""
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def edgeDragStart(self, item):
        if DEBUG:
            print('Clicked :')
            print_items(item)

        # Store previous edge and socket if existing
        self.previousEdge = item.socket.edge
        self.last_start_socket = item.socket
        # Create a new edge
        self.dragEdge = Edge(self.grScene.scene, item.socket, None, EDGE_TYPE_BEZIER)
        if DEBUG:
            print('Dragging :')
            print_items(self.dragEdge.grEdge)
            if self.previousEdge is not None:
                print('Previous edge :')
                print_items(self.previousEdge.grEdge)

    def edgeDragEnd(self, item):
        """Return True if skip the rest of the code"""

        self.mode = MODE_NOOP
        if type(item) is QNEGraphicsSocket and item.socket is not self.dragEdge.start_socket:
            if item.socket.hasEdge():
                item.socket.edge.remove()

            if self.previousEdge is not None:
                if DEBUG:
                    print('Removing previous edge :')
                    print_items(self.previousEdge)
                self.previousEdge.remove()
                # self.previousEdge = None

            self.dragEdge.start_socket = self.last_start_socket
            self.dragEdge.end_socket = item.socket
            self.dragEdge.start_socket.setConnectedEdge(self.dragEdge)
            self.dragEdge.end_socket.setConnectedEdge(self.dragEdge)
            self.dragEdge.updatePositions()
            self.grScene.scene.history.storeHistory('Created new edge by dragging', setModified=True)
            if DEBUG:
                print('New edge')
                print_items(self.dragEdge.grEdge)
                if self.previousEdge is not None:
                    print('Previous edge')
                    print_items(self.previousEdge.grEdge)

            return True

        if DEBUG:
            print('Removing :')
            print_items(self.dragEdge.grEdge)
        self.dragEdge.remove()

        if self.previousEdge is not None:
            if DEBUG:
                print('Previous edge :')
                print_items(self.previousEdge.grEdge)
            self.previousEdge.start_socket.edge = self.previousEdge

        return False

    def distanceBetweenClickAndRelease(self, event):
        """Measures if we are too far from the last LMB click scene position"""
        new_lmb_click_scene_pos = self.mapToScene(event.pos())
        dist_scene_pos = new_lmb_click_scene_pos - self.last_lmb_click_scene_pos
        return dist_scene_pos.x() ** 2 + dist_scene_pos.y() ** 2 >= EDGE_DRAG_START_THRESHOLD ** 2
