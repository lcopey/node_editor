from PyQt5.QtCore import Qt, QIODevice, QDataStream
from PyQt5.QtGui import QCloseEvent, QDropEvent, QDragEnterEvent, QPixmap, QContextMenuEvent, QIcon
from PyQt5.QtWidgets import QGraphicsProxyWidget, QMenu, QAction
from node_editor.node_edge import EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT
from .data_conf import *
from .data_node_base import *

from node_editor.node_node import Node
from node_editor.node_editor_widget import NodeEditorWidget
from node_editor.node_graphics_view import MODE_EDGE_DRAG
from node_editor.utils import dumpException

DEBUG = False
DEBUG_CONTEXT = False


class DataSubWindow(NodeEditorWidget):
    def __init__(self):
        super().__init__()
        # self.setAttribute(Qt.WA_DeleteOnClose)

        self.setTitle()
        self.initNewNodeActions()
        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.history.addHistoryRestoredListener(self.onHistoryRestored)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        self.scene.setNodeClassSelector(self.getNodeClassFromData)

        self._close_event_listeners = []

    def initNewNodeActions(self):
        self.node_actions = {}
        keys = list(DATA_NODES.keys())
        keys.sort()
        for key in keys:
            node = DATA_NODES[key]
            self.node_actions[node.op_code] = QAction(QIcon(node.icon), node.op_title)
            self.node_actions[node.op_code].setData(node.op_code)

    def initNodesContextMenu(self):
        context_menu = QMenu(self)
        keys = list(DATA_NODES.keys())
        keys.sort()
        for key in keys:
            context_menu.addAction(self.node_actions[key])
        return context_menu

    def onHistoryRestored(self):
        self.doEvalOutputs()

    def doEvalOutputs(self):
        # eval all output nodes
        for node in self.scene.nodes:
            if node.__class__.__name__ == 'CalcNodeOutput':
                node.eval()

    def getNodeClassFromData(self, data):
        if 'op_code' not in data:
            return Node
        return get_call_from_opcode(data['op_code'])

    def fileLoad(self, filename: str) -> bool:
        if super().fileLoad(filename):
            self.doEvalOutputs()
            return True
        return False

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())

    def addCloseEventListener(self, callback: 'function'):
        self._close_event_listeners.append(callback)

    def closeEvent(self, event):
        for callback in self._close_event_listeners:
            callback(self, event)

    def onDragEnter(self, event: QDragEnterEvent):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            if DEBUG: print('drag enter accepted')
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

                event.setDropAction(Qt.MoveAction)
                event.accept()

            except Exception as e:
                dumpException(e)
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
        markDirtyDescendant = context_menu.addAction('Mark Descendant Dirty')
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

        if selected and action == markDirtyAct:
            selected.markDirty()
        elif selected and action == markInvalidAct:
            selected.markInvalid()
        elif selected and action == unmarkInvalidAct:
            selected.markInvalid(False)
        elif selected and action == markDirtyDescendant:
            selected.markDescendantDirty(True)
        elif selected and action == evalAct:
            val = selected.eval()
            if DEBUG_CONTEXT: print(val)

    def determine_target_socket_of_node(self, was_dragged_flag, new_calc_node):
        target_socket = None
        if was_dragged_flag:
            if len(new_calc_node.inputs) > 0:
                target_socket = new_calc_node.inputs[0]
        else:
            if len(new_calc_node.outputs) > 0:
                target_socket = new_calc_node.outputs[0]

        return target_socket

    def finish_new_node_state(self, new_calc_node):
        self.scene.doDeselectItems()
        new_calc_node.grNode.doSelect(True)
        new_calc_node.grNode.onSelected()

    def handleNewNodeContextMenu(self, event: QContextMenuEvent):
        if DEBUG_CONTEXT: print('Context: New Node')
        context_menu = self.initNodesContextMenu()

        action = context_menu.exec_(self.mapToGlobal(event.pos()))  # draw to scene and get the selected action

        if action is not None:
            new_calc_node = get_call_from_opcode(action.data())(self.scene)
            scene_pos = self.scene.getView().mapToScene(event.pos())
            new_calc_node.setPos(scene_pos.x(), scene_pos.y())

            if self.scene.getView().mode == MODE_EDGE_DRAG:
                # in dragging edge mode, connect the current edge to the first input
                target_socket = self.determine_target_socket_of_node(
                    self.scene.getView().dragging.drag_start_socket.is_output,
                    new_calc_node)
                if target_socket is not None:
                    self.scene.getView().dragging.edgeDragEnd(target_socket.grSocket)
                    self.finish_new_node_state(new_calc_node)

                # select the newly create node
                new_calc_node.doSelect(True)

            else:
                self.scene.history.storeHistory(f'Created {new_calc_node.__class__.__name__}')
