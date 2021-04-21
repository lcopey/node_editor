from node_editor.node_node import Node
from .data_node_graphics_base import VizGraphicsNode
from node_editor.node_socket import SocketPosition
from node_editor.utils import dumpException
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from node_editor.node_socket import Socket
    from node_editor.node_scene import Scene

DEBUG = True


class Configurable:
    """Configurable node implement PropertiesWidget methods"""

    def __init__(self, **kwargs):
        super(Configurable, self).__init__()
        if DEBUG:
            print('>Configurable', 'Instantiating')
        self.propertiesWidget = None
        self.initPropertiesWidget()

    def initPropertiesWidget(self):
        """To be overridden, defines an attribute named properties_widget used in the properties toolbar"""
        raise NotImplementedError

    def hasPropertiesWidget(self):
        return self.propertiesWidget is not None


class DataNode(Node):
    GraphicsNode_class = VizGraphicsNode
    NodeContent_class = None
    icon = ""
    op_title = 'Undefined'
    content_label = ''
    content_label_objname = 'calc_node_bg'
    """Class representing the `DataNode`"""

    def __init__(self, scene: 'Scene', inputs=None, outputs=None):
        """Instantiate a `DataNode` which is a subclass of :class:`~node_editor.node_node.Node`

        **Instance Attributes**

        - scene : reference to the :class:`~node_editor.node_scene.Scene`
        - grNode : by default, reference to the :class:`~data_node_graphics_base.rst.VizGraphicsNode`
        - input_socket_position : :class:`~node_socket.SocketPosition`
        - output_socket_position : :class:`~node_socket.SocketPosition`

        Parameters
        ----------
        scene: Scene
            reference to the :class:`~node_editor.node_scene.Scene`
        inputs: List[int]
        outputs: List[int]
        """
        if outputs is None:
            outputs = [1]
        if inputs is None:
            inputs = [2, 2]
        super(DataNode, self).__init__(scene, title=self.__class__.op_title, inputs=inputs, outputs=outputs,)

        self.input_socket_position: Optional[SocketPosition] = None
        self.output_socket_position: Optional[SocketPosition] = None

        # Nodes are dirty by default
        self.value = None
        self.markDirty()

    @classmethod
    def getOpCode(cls):
        """Return the op_code of the node.

        Corresponds to the class name definition as it should be unique.
        Helper function to work with NodeFactory class"""
        return cls.__name__

    def print(self, *args):
        if DEBUG:
            print(f'> {self.__class__.__name__}', *args)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = SocketPosition.MiddleLeft
        self.output_socket_position = SocketPosition.MiddleRight

    def getNodeSettings(self) -> dict:
        """To be overridden - should returns the node settings"""
        return dict()

    def restoreNodeSettings(self, data: dict) -> bool:
        """To be overridden - restore the node settings"""
        return False

    def serialize(self) -> dict:
        """Serialize the node.

        Call :py:meth:`~data_node_base.DataNode.getNodeSettings` to retrieve the node specific settings.
        Returns
        -------
        dict
            Dictionary of node settings and parameters to serialize
        """
        res = super().serialize()
        res['op_code'] = self.__class__.getOpCode()
        res['node_settings'] = self.getNodeSettings()
        self.print('serialize')
        return res

    def deserialize(self, data: dict, hashmap: dict = None, restore_id: bool = True) -> bool:
        """Deserialize the node with corresponding data

        Parameters
        ----------
        data: dict
            Serialized settings of the node
        hashmap: dict
        restore_id: bool
            if ``True``, set the 'id' attribute to data['id'] else a new object with its own id is generated.

        Returns
        -------
        bool
            ``True`` if successful, ``False`` otherwise

        """
        if hashmap is None:
            hashmap = {}
        res = super().deserialize(data, hashmap, restore_id)
        # restore the node settings
        if data['node_settings'] != dict():
            res &= self.restoreNodeSettings(data)
        print("Deserialize DataNode {}: res : {}".format(self.__class__.__name__, res))
        return res

    def forcedEval(self) -> Any:
        """Force evaluation of the current `DataNode`.

        Returns
        -------
        Any


        """
        self.markDirty(True)
        return self.eval(force=True)

    def eval(self, force: bool = False) -> Any:
        """Evaluate this `Node`.

        Return cached value in case no change was detected. Evaluation can be forced by setting Force to ``True``.
        Otherwise, evaluate this `Node` by calling :py:meth:`~data_node_base.DataNode.evalImplementation`.
        In case of ValueError, set the node and their children as dirty.
        Any other error will set the node and their children as invalid
        Parameters
        ----------
        force: bool
            ``True`` Force evaluation of this `Node`.

        Returns
        -------
        Any

        """
        if not self.isDirty() and not self.isInvalid():
            self.print('Dirty : ', self.isDirty(), 'Invalid : ', self.isInvalid())
            self.print(f" _> return cached {self.__class__.__name__} value {self.value}")
            return self.value

        try:
            # By default, undirty and valid the node
            # self.markDirty(False)
            # self.markInvalid(False)
            val = self.evalImplementation(force=force)
            return val

        except ValueError as e:
            self.markDirty()
            self.setToolTip(str(e))
            self.markDescendantDirty()

        except Exception as e:
            self.markInvalid()
            self.setToolTip(str(e))
            dumpException(e)

    def evalImplementation(self, force: bool = False):
        """Evaluation implementation of the current `DataNode`.


        Evaluation of the node usually implements the following steps :
            - get values of the inputs
            - handle errors :
                - mark invalid and DescendantDirty
                - set tooltip with error message
            - reset the states of the Node : un-Dirty and Valid
            - store the current evaluation in self.value
            - reset tooltip
            - markDescendantDirty(True) :py:meth:'~data_node_base.DataNode.markDescendantInvalid(False)'
            - evaluate the children of the `Node`
            - return current evaluation

        Returns
        -------

        """
        raise NotImplementedError

    def onInputChanged(self, socket: 'Socket') -> Any:
        """Event called when an `Edge` is connected to the inputs

        Parameters
        ----------
        socket: 'Socket'

        Returns
        -------

        """
        self.print(f'{self.__class__.__name__}::onInputChanged')
        self.markDirty()
        return self.eval()
