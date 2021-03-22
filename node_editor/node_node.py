from collections import OrderedDict
from .node_serializable import Serializable
from .node_graphics_node import GraphicsNode
from node_editor.node_content_widget import NodeContentWidget
from .node_socket import Socket, SocketPosition
from .node_status import GraphicsStatus
from .utils import dumpException, return_simple_id

from typing import TYPE_CHECKING, List, Tuple, Union

if TYPE_CHECKING:
    from .node_scene import Scene

DEBUG = True


class Node(Serializable):
    GraphicsNode_class = GraphicsNode
    NodeContent_class = NodeContentWidget
    GraphicsStatus_class = GraphicsStatus
    Socket_class = Socket
    """Class representing the `Node`"""

    def __init__(self, scene: 'Scene', title: str = 'Undefined Node', inputs: List[int] = None,
                 outputs: List[int] = None):
        """Instantiate a new `Node` and add it to the `Graphical Scene`

        Instance Attributes
        -------------------
            scene - reference to the :class:`~node_editor.node_scene.Scene`
            grNode - reference to the :class:`~node_editor.node_graphics_node.GraphicsNode`

        Parameters
        ----------
        scene : :class:`~node_editor.node_scene.Scene`
            Reference to the :class:`~node_editor.node_scene.Scene`
        title : str
            Name of the node displayed on the upper side of the `Node`
        inputs : list of :class:`~node_editor.node_socket.Socket`
        outputs : list of :class:`~node_editor.node_socket.Socket`
        """
        super().__init__()

        if inputs is None:
            inputs = []
        if outputs is None:
            outputs = []

        # init attributes
        self.grStatus: Union[Node.GraphicsStatus_class, None] = None

        # reference to the actual scene
        self.scene = scene
        self.title = title

        self.content: Union[NodeContentWidget, None] = None
        self.grNode: Union[GraphicsNode, None] = None
        self.initInnerClasses()
        self.initSettings()

        # add the node to the scene and to the graphical scene
        self.scene.addNode(self)  # basically append self to the list of nodes in Scene
        self.scene.grScene.addItem(self.grNode)  # add item to the graphical scene, so it can be displayed

        # instantiate sockets
        self.inputs: List[Union['Socket', None]] = []
        self.outputs: List[Union['Socket', None]] = []
        self.initSockets(inputs, outputs)

        # dirty and evaluation
        self._is_dirty = False
        self._is_invalid = False

    def __str__(self):
        return return_simple_id(self, 'Node')

    # convenience function to update and get the position of the node in the graphical scene
    @property
    def pos(self):
        return self.grNode.pos()

    def setPos(self, x, y):
        self.grNode.setPos(x, y)

    @property
    def width(self):
        return self.grNode.width

    @width.setter
    def width(self, value):
        self.grNode.width = value

    @property
    def height(self):
        return self.grNode.height

    @height.setter
    def height(self, value):
        self.grNode.height = value

    @property
    def min_width(self):
        return self.grNode.min_width

    @min_width.setter
    def min_width(self, value):
        self.grNode.min_width = value

    @property
    def min_height(self):
        return self.grNode.min_height

    @min_height.setter
    def min_height(self, value):
        self.grNode.min_height = value

    @property
    def resizeable(self):
        return self.grNode.resizeable

    @resizeable.setter
    def resizeable(self, value):
        self.grNode.resizeable = value

    @property
    def title(self, ) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value
        if hasattr(self, 'grNode'):
            self.grNode.title = self._title

    def initInnerClasses(self):
        """
        Instantiate innerclasses :
        - node_content_class : by default :class:`~node_editor.node_content_widget.NodeContentWidget`
        - graphics_node_class : by default :class:`~node_editor.node_graphics_node.GraphicsNode`

        Uses internal methodes `getNodeContentClass` and `getGraphicsNodeClass` to obtain the definition
         of the above two classes
        """
        # Reference to the content
        try:
            node_content_class = self.getNodeContentClass()
            graphics_node_class = self.getGraphicsNodeClass()
            graphics_status_class = self.getGraphicsStatusClass()
            if node_content_class is not None:
                self.content = node_content_class(self)
            if graphics_node_class is not None:
                self.grNode = graphics_node_class(self)
            if graphics_status_class is not None:
                self.grStatus = graphics_status_class(self)
        except Exception as e:
            dumpException(e)

    def initSettings(self):
        self.input_socket_position = SocketPosition.BottomLeft
        self.output_socket_position = SocketPosition.TopRight
        self.input_multi_edged = False
        self.output_multi_edged = True

    def initSockets(self, inputs: list, outputs: list, reset=True):
        """"Create sockets for inputs and outputs"""

        if reset:
            # clear old sockets
            if hasattr(self, 'inputs') and hasattr(self, 'outputs'):
                # remove grSockets from scene
                for socket in self.inputs + self.outputs:
                    self.scene.grScene.removeItem(socket.grSocket)
                self.inputs = []
                self.outputs = []

        for n, item in enumerate(inputs):
            socket = Socket(node=self, index=n, position=self.input_socket_position, socket_type=item,
                            multi_edges=self.input_multi_edged,
                            count_on_this_node_side=len(inputs), is_input=True)
            self.inputs.append(socket)

        for n, item in enumerate(outputs):
            socket = Socket(node=self, index=n, position=self.output_socket_position, socket_type=item,
                            multi_edges=self.output_multi_edged,
                            count_on_this_node_side=len(outputs), is_input=False)
            self.outputs.append(socket)

    def getNodeContentClass(self):
        return self.__class__.NodeContent_class

    def getGraphicsNodeClass(self):
        return self.__class__.GraphicsNode_class

    def getGraphicsStatusClass(self):
        return self.__class__.GraphicsStatus_class

    def getSocketPosition(self, index: int, position: SocketPosition, num_out_of: int = 1) -> List[float]:
        """Helper function - returns the position of a socket in pixels relative to the `Graphical Node`

        Parameters
        ----------
        index : ```int```
            Index of the socket in the list
        position : SocketPosition
            One of enumeration
        num_out_of : ```int```
            total number of `Socket` on this position

        Returns
        -------
        ```list```
            x, y position relative to the node
        """
        return self.grNode.getSocketPosition(index, position, num_out_of)

    def getSocketScenePosition(self, socket: 'Socket') -> Tuple[Union[None, float], Union[None, float]]:
        """Helper function - returns the position of a socket in pixels relative to the `Graphical Scene`

        Parameters
        ----------
        socket : `Socket`
            Socket to return position from
        Returns
        -------
        ```tuple```
            x, y position relative to the node
        """
        nodepos = self.grNode.pos()
        socketpos = self.getSocketPosition(socket.index, socket.position, socket.count_on_this_node_side)
        # return position offseted of node position
        return nodepos.x() + socketpos[0], nodepos.y() + socketpos[1]

    def getSockets(self) -> List['Socket']:
        """Return the list of sockets for this `Node`"""
        return self.inputs + self.outputs

    def isSelected(self):
        """Returns ```True``` if current `Node` is selected"""
        return self.grNode.isSelected()

    def onEdgeConnectionChanged(self, new_edge):
        self.print(f'{self.__class__.__name__}::onEdgeConnectionChanged {new_edge}')
        pass

    def onInputChanged(self, socket: 'Socket'):
        self.print(f'{self.__class__.__name__}::onInputChanged {socket}')
        self.markDirty()
        self.markDescendantDirty()

    def onDeserialized(self, data: dict):
        """Event manually called when this node was deserialized."""
        pass

    def onDoubleClicked(self, event):
        """Event handling double click on Graphics Node in `Scene`"""
        pass

    def onSelected(self):
        """onSelected event"""
        self.print('on Selected event')

    def onDelected(self):
        self.print('on deSelected event')

    def doSelect(self, new_state=True):
        self.grNode.doSelect(new_state)

    def updateConnectedEdges(self):
        for socket in self.inputs + self.outputs:
            for edge in socket.edges:
                edge.updatePositions()

    def remove(self):
        self.print('> Removing Node', self)
        self.print(' - remove all edges from sockets', self)
        for socket in (self.inputs + self.outputs):
            # TODO revisit the remove edge method ???
            for edge in socket.edges.copy():
                self.print('   - removing edge ', edge, ' from socket ', socket)
                edge.remove()

        self.print(' - remove grNode', self)
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        self.print(' - remove node from scene', self)
        self.scene.removeNode(self)
        self.print(' - everything was done')

    # node evaluation function
    def isDirty(self):
        return self._is_dirty

    def isInvalid(self):
        return self._is_invalid

    def markDirty(self, new_value=True):
        """Mark this `Node` as `Dirty`. See :ref:`evaluation` for more

        Parameters
        ----------
        new_value : bool
            ``True`` if this `Node` should be `Dirty`. ``False`` if you want to un-dirty this `Node`
        """
        # If the value change, update the graphical status
        graphics_update = True
        if self._is_dirty == new_value:
            graphics_update = False

        self._is_dirty = new_value
        if graphics_update and self.grStatus:
            self.grStatus.update()

        if self._is_dirty:
            self.onMarkedDirty()

    def markChildrenDirty(self, new_value=True):
        """Mark all first level children of this `Node` to be `Dirty`. Not this `Node` it self. Not other descendants

        Parameters
        ----------
        new_value : bool
            ``True`` if children should be `Dirty`. ``False`` if you want to un-dirty children
        """
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)

    def markDescendantDirty(self, new_value: bool = True):
        """Mark all children and descendants of this `Node` to be `Invalid`. Not this `Node` it self

        Parameters
        ----------
        new_value : bool
            ``True`` if children and descendants should be `Invalid`.
            ``False`` if you want to make children and descendants valid
        """
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)
            other_node.markDescendantDirty(new_value)

    def markInvalid(self, new_value=True):
        """Mark this `Node` as `Invalid`. See :ref:`evaluation` for more

        Parameters
        ----------
        new_value : bool
            ``True`` if this `Node` should be `Invalid`. ``False`` if you want to make this `Node` valid
        """
        graphics_update = True
        if self._is_invalid == new_value:
            graphics_update = False

        self._is_invalid = new_value
        if graphics_update and self.grStatus:
            self.grStatus.update()

        if self._is_invalid:
            self.onMarkedInvalid()

    def markChildrenInvalid(self, new_value=True):
        """Mark all first level children of this `Node` to be `Invalid`. Not this `Node` it self. Not other descendants

        Parameters
        ----------
        new_value : bool
            ``True`` if children should be `Invalid`. ``False`` if you want to make children valid
        """
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)

    def markDescendantInvalid(self, new_value: bool = True):
        """Mark all children and descendants of this `Node` to be `Invalid`. Not this `Node` it self

        Parameters
        ----------
        new_value : bool
            ``True`` if children and descendants should be `Invalid`.
            ``False`` if you want to make children and descendants valid
        """
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)
            other_node.markDescendantInvalid(new_value)

    def onMarkedDirty(self):
        """Called when this `Node` has been marked as `Dirty`. This method is supposed to be overridden"""
        pass

    def onMarkedInvalid(self):
        """Called when this `Node` has been marked as `Invalid`. This method is supposed to be overridden"""
        pass

    def eval(self, ):
        """Evaluate this `Node`. This method is supposed to be overriden."""
        self.markDirty(False)
        self.markInvalid(False)
        return 0

    # traversing nodes functions

    def evalChildren(self):
        """Evaluate all children of this `Node`"""
        for node in self.getChildrenNodes():
            node.eval()

    def getChildrenNodes(self):
        """Retrieve all first-level children connected to this `Node` `Outputs`

        Returns
        -------
        List[:class:`~nodeeditor.node_node.Node`]
            list of `Nodes` connected to this `Node` from all `Outputs`

        """
        if not self.outputs:
            return []
        other_nodes = []
        for output in self.outputs:
            for edge in output.edges:
                other_node = edge.getOtherSocket(output).node
                other_nodes.append(other_node)
        return other_nodes

    def getInput(self, index: int = 0) -> Union['Node', None]:
        """Get the **first** `Node` connected to the Input specified by index

        Parameters
        ----------
        index : ``int``
            Order number of the `Input Socket`

        Returns
        -------
        :class: `~node_editor.node_node.Node` or None
            :class: `~node_editor.node_node.Node` which is connected to the specified `Input Socket`
        """
        try:
            input_socket = self.inputs[index]
            if len(input_socket.edges) == 0:
                return None
            connecting_edge = self.inputs[index].edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node
        except IndexError:
            print(f'Exception : Trying to get input, but none is attached to {self}')
            return None
        except Exception as e:
            dumpException(e)
            return None

    def getInputWithSocket(self, index: int = 0) -> Union[Tuple['Node', 'Socket'], None]:
        try:
            input_socket = self.inputs[index]
            if len(input_socket) == 0:
                return None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node, other_socket

        except IndexError:
            print(f'Exception : Trying to get input, but none is attached to {self}')
            return None
        except Exception as e:
            dumpException(e)
            return None

    def getInputWithSocketIndex(self, index: int = 0) -> Union[Tuple['Node', int], None]:
        try:
            input_socket = self.inputs[index]
            if len(input_socket) == 0:
                return None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node, other_socket.index

        except IndexError:
            print(f'Exception : Trying to get input, but none is attached to {self}')
            return None
        except Exception as e:
            dumpException(e)
            return None

    def getInputs(self, index=0):
        """Get the list of `Nodes` connected to the input `Socket` `Node`"""
        ins = []
        for edge in self.inputs[index].edges:
            other_socket = edge.getOtherSocket(self.inputs[index])
            ins.append(other_socket.node)
        return ins

    def getOutputs(self, index=0):
        """Get the list of `Nodes` connected to the output `Socket` `Node`"""
        outs = []
        for edge in self.outputs[index].edges:
            other_socket = edge.getOtherSocket(self.outputs[index])
            outs.append(other_socket.node)
        return outs

    def setToolTip(self, text):
        """Assign the tooltip to the `Graphical Status` if available and the `Graphical Node`"""
        if self.grStatus:
            self.grStatus.setToolTip(text)
        self.grNode.setToolTip(text)

    def print(self, *args):
        if DEBUG:
            print('>Node :', *args)

    # serialization function

    def serialize(self):
        inputs = [socket.serialize() for socket in self.inputs]
        outputs = [socket.serialize() for socket in self.outputs]

        result = OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('pos_x', self.grNode.scenePos().x()),
            ('pos_y', self.grNode.scenePos().y()),
            ('width', self.grNode.width),
            ('height', self.grNode.height),
            ('resizeable', self.grNode.resizeable),
            ('inputs', inputs),
            ('outputs', outputs),
        ])
        if self.content is not None:
            ser_content = self.content.serialize() if isinstance(self.content, Serializable) else {}
            result['content'] = ser_content

        return result

    def deserialize(self, data: dict, hashmap=None, restore_id: bool = True):
        if hashmap is None:
            hashmap = {}
        try:
            if restore_id:
                self.id = data['id']
            hashmap[data['id']] = self

            self.setPos(data['pos_x'], data['pos_y'])  # Restore the position of the node
            self.title = data['title']  # Restore the title
            if 'width' in data:
                self.width = data['width']
            if 'height' in data:
                self.height = data['height']
            if 'resizeable' in data:
                self.resizeable = data['resizeable']
            self.grNode.updateLayout()

            # Deserialize the Sockets
            data['inputs'].sort(key=lambda value: value['index'] + value['position'] * 1e3)
            data['outputs'].sort(key=lambda value: value['index'] + value['position'] * 1e3)
            num_inputs = len(data['inputs'])
            num_outputs = len(data['outputs'])

            # Restore the Socket, either instantiate a new Socket or update existing one when found
            for socket_data in data['inputs']:
                found = None
                for socket in self.inputs:
                    if socket.index == socket_data['index']:
                        found = socket
                        break

                if found is None:
                    found = self.__class__.Socket_class(
                        node=self, index=socket_data['index'],
                        position=SocketPosition(socket_data['position']),
                        socket_type=socket_data['socket_type'],
                        count_on_this_node_side=num_inputs,
                        is_input=True)
                    self.inputs.append(found)
                found.deserialize(socket_data, hashmap, restore_id)

            for socket_data in data['outputs']:
                found = None
                for socket in self.outputs:
                    if socket.index == socket_data['index']:
                        found = socket
                        break
                if found is None:
                    found = self.__class__.Socket_class(
                        node=self, index=socket_data['index'],
                        position=SocketPosition(socket_data['position']),
                        socket_type=socket_data['socket_type'],
                        count_on_this_node_side=num_outputs,
                        is_input=False)
                    self.outputs.append(found)
                found.deserialize(socket_data, hashmap, restore_id)

            # deserialize the content of the node
            if self.content is not None and isinstance(self.content, Serializable):
                res = self.content.deserialize(data['content'], hashmap)
                return res

        except Exception as e:
            dumpException(e)

        return True
