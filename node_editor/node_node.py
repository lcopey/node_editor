from collections import OrderedDict
from .node_serializable import Serializable
from .node_graphics_node import GraphicsNode
from node_editor.node_content_widget import QNENodeContentWidget
from .node_socket import Socket, SocketPosition
from .utils import dumpException, print_func_name, return_simple_id

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node_scene import Scene

DEBUG = False


class Node(Serializable):
    GraphicsNode_class = GraphicsNode
    NodeContent_class = QNENodeContentWidget
    Socket_class = Socket
    """Class representing the `Node`"""

    def __init__(self, scene: 'Scene', title='Undefined Node', inputs=[], outputs=[]):
        """Instantiate a new `Node` and add it to the `Graphical Scene`

        Instance Attributes:
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
        # reference to the actual scene
        self.scene = scene
        self.title = title

        self.content = None
        self.grNode = None
        self.initInnerClasses()
        self.initSettings()

        # add the node to the scene and to the graphical scene
        self.scene.addNode(self)  # basically append self to the list of nodes in Scene
        self.scene.grScene.addItem(self.grNode)  # add item to the graphical scene, so it can be displayed

        # instantiate sockets
        self.inputs = []
        self.outputs = []
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
    def resizeable(self):
        return self.grNode.resizeable

    @resizeable.setter
    def resizeable(self, value):
        self.grNode.resizeable = value

    @property
    def title(self, ):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        if hasattr(self, 'grNode'):
            self.grNode.title = self._title

    def initInnerClasses(self):
        """
        Instantiate innerclasses :
        - node_content_class : by default :class:`~node_editor.node_content_widget.QNENodeContentWidget`
        - graphics_node_class : by default :class:`~node_editor.node_graphics_node.GraphicsNode`

        Uses internal methodes `getNodeContentClass` and `getGraphicsNodeClass` to obtain the definition
         of the above two classes
        """
        # Reference to the content
        node_content_class = self.getNodeContentClass()
        graphics_node_class = self.getGraphicsNodeClass()
        if node_content_class is not None:
            self.content = node_content_class(self)
        if graphics_node_class is not None:
            self.grNode = graphics_node_class(self)

    def initSettings(self):
        self.socket_spacing = 22
        self.input_socket_position = SocketPosition.LEFT_BOTTOM
        self.output_socket_position = SocketPosition.RIGHT_TOP
        self.input_multi_edged = False
        self.output_multi_edged = True
        self.socket_offsets = {
            SocketPosition.LEFT_BOTTOM: -1,
            SocketPosition.LEFT_CENTER: -1,
            SocketPosition.LEFT_TOP: -1,
            SocketPosition.RIGHT_BOTTOM: 1,
            SocketPosition.RIGHT_CENTER: 1,
            SocketPosition.RIGHT_TOP: 1,
        }

    def initSockets(self, inputs, outputs, reset=True):
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

    def getSocketPosition(self, index: int, position: SocketPosition, num_out_of: int = 1) -> '(x, y)':
        """Helper function - returns the position of a socket in pixels relative to the node

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
        if position in (SocketPosition.LEFT_TOP, SocketPosition.LEFT_CENTER, SocketPosition.LEFT_BOTTOM):
            x = self.socket_offsets[position]
        else:
            x = self.grNode.width + self.socket_offsets[position]

        if position in (SocketPosition.LEFT_BOTTOM, SocketPosition.RIGHT_BOTTOM):
            # start from bottom
            y = self.grNode.height - (
                    index * self.socket_spacing + self.grNode.title_vertical_padding + self.grNode.edge_roundness)
        elif position in (SocketPosition.LEFT_CENTER, SocketPosition.RIGHT_CENTER):
            num_sockets = num_out_of
            node_height = self.grNode.height
            top_offset = self.grNode.title_height + 2 * self.grNode.title_vertical_padding + self.grNode.edge_padding
            available_height = node_height - top_offset

            total_height_of_all_socket = num_sockets * self.socket_spacing

            new_top = available_height - total_height_of_all_socket

            # y = top_offset + index * self.socket_spacing + new_top / 2
            y = top_offset + available_height / 2. + (index - 0.5) * self.socket_spacing - \
                (num_sockets - 1) * self.socket_spacing / 2

        elif position in (SocketPosition.LEFT_TOP, SocketPosition.RIGHT_TOP):
            # start from top
            y = index * self.socket_spacing + self.grNode.title_height + self.grNode.title_vertical_padding + self.grNode.edge_roundness
        else:
            y = 0

        return [x, y]

    def getSocketScenePosition(self, socket: 'Socket') -> '(x, y)':
        nodepos = self.grNode.pos()
        socketpos = self.getSocketPosition(socket.index, socket.position, socket.count_on_this_node_side)
        return (nodepos.x() + socketpos[0], nodepos.y() + socketpos[1])

    def isSelected(self):
        """Returns ```True``` if current `Node` is selected"""
        return self.grNode.isSelected()

    def onEdgeConnectionChanged(self, new_edge):
        if DEBUG: print(f'{self.__class__.__name__}::onEdgeConnectionChanged {new_edge}')
        pass

    def onInputChanged(self, socket: 'Socket'):
        if DEBUG: print(f'{self.__class__.__name__}::onInputChanged {socket}')
        self.markDirty()
        self.markDescendantDirty()

    def onDeserialized(self, data: dict):
        """Event manually called when this node was deserialized."""
        pass

    def onDoubleClicked(self, event):
        """Event handling double click on Graphics Node in `Scene`"""
        pass

    def doSelect(self, new_state=True):
        self.grNode.doSelect(new_state)

    def updateConnectedEdges(self):
        for socket in self.inputs + self.outputs:
            for edge in socket.edges:
                edge.updatePositions()

    def remove(self):
        if DEBUG: print('> Removing Node', self)
        if DEBUG: print(' - remove all edges from sockets', self)
        for socket in (self.inputs + self.outputs):
            # if socket.hasEdge():
            for edge in socket.edges:
                if DEBUG: print('   - removing edge ', edge, ' from socket ', socket)
                edge.remove()

        if DEBUG: print(' - remove grNode', self)
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        if DEBUG: print(' - remove node from scene', self)
        self.scene.removeNode(self)
        if DEBUG: print(' - everything was done')

    # node evaluation function
    def isDirty(self):
        return self._is_dirty

    def markDirty(self, new_value=True):
        self._is_dirty = new_value
        if self._is_dirty:
            self.onMarkedDirty()

    def markChildrenDirty(self, new_value=True):
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)

    def markDescendantDirty(self, new_value=True):
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)
            other_node.markChildrenDirty(new_value)

    def isInvalid(self):
        return self._is_invalid

    def markInvalid(self, new_value=True):
        self._is_invalid = new_value
        if self._is_invalid:
            self.onMarkedInvalid()

    def markChildrenInvalid(self, new_value=True):
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)

    def markDescendantInvalid(self, new_value=True):
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)
            other_node.markChildrenInvalid(new_value)

    def onMarkedDirty(self):
        pass

    def onMarkedInvalid(self):
        pass

    def eval(self, index=0):
        """Evaluated this `Node`. This method is supposed to be overriden."""
        self.markDirty(False)
        self.markInvalid(False)
        return 0

    # traversing nodes functions

    def evalChildren(self):
        for node in self.getChildrenNodes():
            node.eval()

    def getChildrenNodes(self):
        if not self.outputs:
            return []
        other_nodes = []
        for output in self.outputs:
            for edge in output.edges:
                other_node = edge.getOtherSocket(output).node
                other_nodes.append(other_node)
        return other_nodes

    def getInput(self, index: int = 0) -> [Socket, None]:
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
            if len(input_socket.edges) == 0: return None
            connecting_edge = self.inputs[index].edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node
        except IndexError:
            print(f'Exception : Trying to get input, but none is attached to {self}')
            return None
        except Exception as e:
            dumpException(e)
            return None

    def getInputWithSocket(self, index: int = 0) -> [('Node', 'Socket'), (None, None)]:
        try:
            input_socket = self.inputs[index]
            if len(input_socket) == 0: return None, None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node, other_socket

        except IndexError:
            print(f'Exception : Trying to get input, but none is attached to {self}')
            return None
        except Exception as e:
            dumpException(e)
            return None

    def getInputWithSocketIndex(self, index: int = 0) -> [('Node', 'Socket'), (None, None)]:
        try:
            input_socket = self.inputs[index]
            if len(input_socket) == 0: return None, None
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
        ins = []
        for edge in self.inputs[index].edges:
            other_socket = edge.getOtherSocket(self.inputs[index])
            ins.append(other_socket.node)
        return ins

    def getOutputs(self, index=0):
        outs = []
        for edge in self.outputs[index].edges:
            other_socket = edge.getOtherSocket(self.outputs[index])
            outs.append(other_socket.node)
        return outs

    # serialization function

    def serialize(self):
        inputs = [socket.serialize() for socket in self.inputs]
        outputs = [socket.serialize() for socket in self.outputs]
        ser_content = self.content.serialize() if isinstance(self.content, Serializable) else {}

        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('pos_x', self.grNode.scenePos().x()),
            ('pos_y', self.grNode.scenePos().y()),
            ('width', self.grNode.width),
            ('height', self.grNode.height),
            ('resizeable', self.grNode.resizeable),
            ('inputs', inputs),
            ('outputs', outputs),
            ('content', ser_content)
        ])

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True):
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

            # Deserialize the Sockets
            data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 1e3)
            data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 1e3)
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
            if isinstance(self.content, Serializable):
                res = self.content.deserialize(data['content'], hashmap)
                return res

        except Exception as e:
            dumpException(e)

        return True
