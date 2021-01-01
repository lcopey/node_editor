from PyQt5.QtCore import Qt, QIODevice, QDataStream
from PyQt5.QtGui import QCloseEvent, QDropEvent, QDragEnterEvent, QPixmap, QContextMenuEvent, QIcon
from PyQt5.QtWidgets import QGraphicsProxyWidget, QMenu, QAction
from node_editor.node_edge import EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT
from .calc_conf import *
from .calc_node_base import *

from node_editor.node_node import Node
from node_editor.node_editor_widget import NodeEditorWidget
from node_editor.utils import dumpException

DEBUG = False
DEBUG_CONTEXT = True


class CalculatorSubWindow(NodeEditorWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setTitle()
        self.initNewNodeActions()
        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        self.scene.setNodeClassSelector(self.getNodeClassFromData)

        self._close_event_listeners = []

    def getNodeClassFromData(self, data):
        if 'op_code' not in data:
            return Node
        return get_call_from_opcode(data['op_code'])

    def initNewNodeActions(self):
        self.node_actions = {}
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys:
            node = CALC_NODES[key]
            self.node_actions[node.op_code] = QAction(QIcon(node.icon), node.op_title)
            self.node_actions[node.op_code].setData(node.op_code)

    def initNodesContextMenu(self):
        context_menu = QMenu(self)
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys:
            context_menu.addAction(self.node_actions[key])
        return context_menu

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())

    def addCloseEventListener(self, callback: 'function'):
        self._close_event_listeners.append(callback)

    def closeEvent(self, event):
        for callback in self._close_event_listeners:
            callback(self, event)

    def onDragEnter(self, event: QDragEnterEvent):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            if DEBUG: print('... denied drag enter event')
            event.setAccepted(False)

    def onDrop(self, event: QDropEvent):
        if DEBUG:
            print('CalcSubWnd : onDrop')
            print(event.mimeData().text())
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            eventData = event.mimeData().data(LISTBOX_MIMETYPE)
            dataStream = QDataStream(eventData, QIODevice.ReadOnly)
            pixmap = QPixmap()
            dataStream >> pixmap
            op_code = dataStream.readInt()
            text = dataStream.readQString()

            mouse_pos = event.pos()
            scene_pos = self.scene.grScene.views()[0].mapToScene(mouse_pos)

            if DEBUG: print(f'DROP: {op_code} {text} at {scene_pos}')

            try:
                node = get_call_from_opcode(op_code)(self.scene)
                node.setPos(scene_pos.x(), scene_pos.y())
                self.scene.history.storeHistory('Create node {}'.format(node.__class__.__name__))
            except Exception as e:
                dumpException(e)
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            if DEBUG: print(' ... drop ignored, not requested format ', LISTBOX_MIMETYPE)
            event.ignore()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        try:
            item = self.scene.getItemAt(event.pos())
            if DEBUG_CONTEXT: print(item)

            if type(item) == QGraphicsProxyWidget:
                item = item.widget()

            if hasattr(item, 'node') or hasattr(item, 'socket'):
                self.handleNodeContextMenu(event)

            elif hasattr(item, 'edge'):
                self.handleEdgeContextMenu(event)

            else:
                self.handleNewNodeContextMenu(event)

            return super().contextMenuEvent(event)

        except Exception as e:
            dumpException(e)

    def handleEdgeContextMenu(self, event: QContextMenuEvent):
        if DEBUG_CONTEXT: print('Context: Edge')
        # define the context menu
        context_menu = QMenu(self)
        bezierAct = context_menu.addAction('Bezier Edge')
        directAct = context_menu.addAction('Direct Edge')
        action = context_menu.exec_(self.mapToGlobal(event.pos()))  # draw to scene and get the selected action

        selected = None
        item = self.scene.getItemAt(event.pos())
        if hasattr(item, 'edge'):
            selected = item.edge

        if selected and action == bezierAct:
            selected.edge_type = EDGE_TYPE_BEZIER

        if selected and action == directAct:
            selected.edge_type = EDGE_TYPE_DIRECT

    def handleNodeContextMenu(self, event: QContextMenuEvent):
        if DEBUG_CONTEXT: print('Context: Node')
        # define the context menu
        context_menu = QMenu(self)
        markDirtyAct = context_menu.addAction('Mark Dirty')
        markInvalidAct = context_menu.addAction('Mark Invalid')
        unmarkInvalidAct = context_menu.addAction('Unmark Invalid')
        evalAct = context_menu.addAction('Eval')

        action = context_menu.exec_(self.mapToGlobal(event.pos()))  # draw to scene and get the selected action

        selected = None
        item = self.scene.getItemAt(event.pos())
        if type(item) == QGraphicsProxyWidget:
            item = item.widget()

        if hasattr(item, 'node'):
            selected = item.node

        if hasattr(item, 'socket'):
            selected = item.socket.node

        if DEBUG_CONTEXT: print('>>Item selected', item)
        # TODO

    def handleNewNodeContextMenu(self, event: QContextMenuEvent):
        if DEBUG_CONTEXT: print('Context: New Node')
        context_menu = self.initNodesContextMenu()

        action = context_menu.exec_(self.mapToGlobal(event.pos()))  # draw to scene and get the selected action

        if action is not None:
            new_calc_node = get_call_from_opcode(action.data())(self.scene)
            scene_pos = self.scene.getView().mapToScene(event.pos())
            new_calc_node.setPos(scene_pos.x(), scene_pos.y())

