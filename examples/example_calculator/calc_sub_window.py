from PyQt5.QtCore import Qt, QIODevice, QDataStream
from PyQt5.QtGui import QCloseEvent, QDropEvent, QDragEnterEvent, QPixmap
from .calc_conf import *

from node_editor.node_node import Node
from node_editor.node_editor_widget import NodeEditorWidget
from node_editor.utils import dumpException

DEBUG = True


class CalculatorSubWindow(NodeEditorWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setTitle()
        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)

        self._close_event_listeners = []

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())

    def addCloseEventListener(self, callback: 'function'):
        self._close_event_listeners.append(callback)

    def closeEvent(self, event):
        for callback in self._close_event_listeners:
            callback(self, event)

    def onDragEnter(self, event: QDragEnterEvent):
        # print('CalcSubWnd : onDragEnter')
        # print(event.mimeData().text())
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            print('... denied drag enter event')
            event.setAccepted(False)

    def onDrop(self, event: QDropEvent):
        # print('CalcSubWnd : onDrop')
        # print(event.mimeData().text())
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

            # TODO Fix me here
            node = Node(self.scene, title=text, inputs=[1,1], outputs=[2])
            node.setPos(scene_pos.x(), scene_pos.y())
            # self.scene.addNode(node) # necessary ?
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            print(' ... drop ignored, not requested format ', LISTBOX_MIMETYPE)
            event.ignore()
