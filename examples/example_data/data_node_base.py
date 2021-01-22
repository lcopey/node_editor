from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QStyleOptionGraphicsItem
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import QRectF
from node_editor.node_node import Node
from node_editor.node_content_widget import NodeContentWidget
from node_editor.node_graphics_node import GraphicsNode
from node_editor.node_socket import SocketPosition
from node_editor.utils import dumpException
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from node_editor.node_socket import Socket
    from node_editor.node_scene import Scene

DEBUG = True


class VizGraphicsNode(GraphicsNode):
    def __init__(self, node: 'Node', parent=None, resizeable=True, min_height=240, min_width=180):
        super().__init__(node=node, parent=parent, resizeable=True, min_height=min_height, min_width=min_width)

    def initSizes(self):
        # Diverse parameters for drawing
        super().initSizes()
        self.edge_roundness = 6.
        self.edge_padding = 0
        self.title_horizontal_padding = 8.
        self.title_vertical_padding = 10

        self.min_width = self.width = 160
        self.min_height = self.height = 74


class OpGraphicsNode(GraphicsNode):
    def __init__(self, node: 'Node', parent=None, resizeable=True, min_height=240, min_width=180):
        super().__init__(node=node, parent=parent, resizeable=False, min_height=min_height, min_width=min_width)
        # TODO subclass paint as a circle
        # TODO subclass getSocketPosition

    def initSizes(self):
        # Diverse parameters for drawing
        super().initSizes()
        self.edge_roundness = 6.
        self.edge_padding = 0
        self.title_horizontal_padding = 8.
        self.title_vertical_padding = 10

        self.min_width = self.width = 100
        self.min_height = self.height = 54


class DataNode(Node):
    icon = ""
    # op_code = 0
    op_title = 'Undefined'
    content_label = ''
    content_label_objname = 'calc_node_bg'

    GraphicsNode_class = VizGraphicsNode
    NodeContent_class = None

    def __init__(self, scene: 'Scene', inputs=[2, 2], outputs=[1]):
        super().__init__(scene, title=self.__class__.op_title, inputs=inputs, outputs=outputs)
        self.value = None
        # Nodes are dirty by default
        self.markDirty()

    @classmethod
    def getOpCode(cls):
        """Return the op_code of the node.

        Corresponds to the class name definition as it should be unique.
        Helper function to work with NodeFactory class"""
        return cls.__name__

    def print(self, *args):
        if DEBUG: print(f'> {self.__class__.__name__}', *args)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = SocketPosition.MiddleLeft
        self.output_socket_position = SocketPosition.MiddleRight

    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.getOpCode()
        self.print('serialize')
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        print("Deserialize DataNode {}: res : {}".format(self.__class__.__name__, res))
        return res

    # def evalOperation(self, i1, i2):
    #     return 123

    def evalImplementation(self):
        raise NotImplementedError

    def eval(self, force=False):
        if not self.isDirty() and not self.isInvalid() and not force:
            self.print('Dirty : ', self.isDirty(), 'Invalid : ', self.isInvalid(), 'Force : ', force)
            self.print(f" _> return cached {self.__class__.__name__} value {self.value}")
            return self.value

        try:
            val = self.evalImplementation()
            return val

        except ValueError as e:
            self.markInvalid()
            self.setToolTip(str(e))
            self.markDescendantDirty()

        except Exception as e:
            self.markInvalid()
            self.setToolTip(str(e))
            dumpException(e)

    def onInputChanged(self, socket: 'Socket'):
        print(f'{self.__class__.__name__}::onInputChanged')
        self.markDirty()
        self.eval()
