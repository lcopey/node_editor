# -*- encoding: utf-8 -*-
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .node_edge import Edge, EDGE_TYPE_BEZIER
from .node_graphics_socket import OUTPUT_SOCKET, INPUT_SOCKET_1
from .node_graphics_view import NodeGraphicsView
from .node_node import Node
from .node_scene import Scene, InvalidFile
from .utils import dumpException


# TODO support for mdi application, implement setTitle as in Node Editor Widget


class NodeEditorWidget(QWidget):
    """The ``NodeEditorWidget`` class"""
    # Allow to specify which scene to use
    Scene_class = Scene
    GraphicsView_class = NodeGraphicsView

    def __init__(self, parent=None):
        super().__init__(parent)

        self.filename = None

        self.initUI()

    def initUI(self):
        """Initialize widget UI"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # create graphics scene
        self.scene = self.__class__.Scene_class()

        # create graphics view
        self.view = self.__class__.GraphicsView_class(self.scene, self)
        # self.view.setScene(self.grScene)
        self.layout.addWidget(self.view)

        # self.addDebugContent()

    def getSelectedItems(self):
        return self.scene.getSelectedItems()

    def getUserFriendlyFilename(self):
        """

        Returns
        -------

        """
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Graph"
        return name + ("*" if self.isModified() else "")

    def isModified(self):
        return self.scene.isModified()

    def isFilenameSet(self):
        return self.filename is not None

    def hasSelectedItems(self) -> bool:
        return len(self.getSelectedItems()) > 0

    def canUndo(self):
        return self.scene.history.canUndo()

    def canRedo(self):
        return self.scene.history.canRedo()

    def fileNew(self):
        self.scene.clear()
        self.filename = None
        self.scene.history.clear()
        self.scene.history.storeInitialHistoryStamp()

    def fileLoad(self, filename: str) -> bool:
        """

        Parameters
        ----------
        filename : str
            Path of the file to load


        Returns
        -------
        bool :
            - True : if the file is successfully loaded
            - False : in case of error

        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.scene.loadFromFile(filename)
            self.filename = filename
            # clear history
            self.scene.history.clear()
            self.scene.history.storeInitialHistoryStamp()
            return True

        except InvalidFile as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, f'Error loading {os.path.basename(filename)}', str(e))
            return False

        except Exception as e:
            dumpException(e)

        finally:
            QApplication.restoreOverrideCursor()

        return False

    def fileSave(self, filename=None):
        if filename is not None:
            self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()
        return True

    def addNodes(self):
        """Add nodes for debug purpose"""
        node1 = Node(self.scene, 'My Node', inputs=[INPUT_SOCKET_1] * 3, outputs=[OUTPUT_SOCKET])
        node2 = Node(self.scene, 'My Node', inputs=[INPUT_SOCKET_1] * 3, outputs=[OUTPUT_SOCKET])
        node3 = Node(self.scene, 'My Node', inputs=[INPUT_SOCKET_1] * 3, outputs=[OUTPUT_SOCKET])
        node1.setPos(-350, -250)
        node2.setPos(-75, 0)
        node3.setPos(200, -150)

        edge1 = Edge(self.scene, node1.outputs[0], node2.inputs[0], edge_type=EDGE_TYPE_BEZIER)
        edge2 = Edge(self.scene, node2.outputs[0], node3.inputs[0], edge_type=EDGE_TYPE_BEZIER)
        edge3 = Edge(self.scene, node1.outputs[0], node3.inputs[2], edge_type=EDGE_TYPE_BEZIER)

        self.scene.history.storeInitialHistoryStamp()
