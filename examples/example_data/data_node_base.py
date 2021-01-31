from node_editor.node_node import Node
from .data_node_graphics_base import VizGraphicsNode
from node_editor.node_socket import SocketPosition
from node_editor.utils import dumpException
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from node_editor.node_socket import Socket
    from node_editor.node_scene import Scene

DEBUG = True


class DataNode(Node):
    icon = ""
    # op_code = 0
    op_title = 'Undefined'
    content_label = ''
    content_label_objname = 'calc_node_bg'

    GraphicsNode_class = VizGraphicsNode
    NodeContent_class = None

    def __init__(self, scene: 'Scene', inputs=None, outputs=None):
        if outputs is None:
            outputs = [1]
        if inputs is None:
            inputs = [2, 2]
        super().__init__(scene, title=self.__class__.op_title, inputs=inputs, outputs=outputs)

        # initPropertiesToolbar in case it exists
        self.initPropertiesToolbar()
        # Nodes are dirty by default
        self.value = None
        self.markDirty()

    def initPropertiesToolbar(self):
        pass

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

    def deserialize(self, data, hashmap=None, restore_id=True):
        if hashmap is None:
            hashmap = {}
        res = super().deserialize(data, hashmap, restore_id)
        print("Deserialize DataNode {}: res : {}".format(self.__class__.__name__, res))
        return res

    def evalImplementation(self):
        """Evaluation implementation of the current `DataNode`.


        Evaluation of the node usually implements the following steps :
            - reset the states of the Node : Dirty and Invalid
            - get values of the inputs
            - handle errors :
                - mark invalid and DescendantDirty
                - set tooltip with error message
            - reset the states of the Node : un-Dirty and Valid
            - store the current evaluation in self.value
            - reset tooltip
            - markDescendantDirty(True) markDescendantInvalid(False)
            - evaluate the children of the `Node`
            - return current evaluation

        Returns
        -------

        """
        raise NotImplementedError

    def eval(self, force=False):
        # TODO replace force with dedicated function doing markDirty + eval
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
        self.print(f'{self.__class__.__name__}::onInputChanged')
        self.markDirty()
        self.eval()
