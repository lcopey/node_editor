from collections import OrderedDict
from .node_serializable import Serializable
from .node_graphics_node import QNEGraphicsNode
from .widgets.node_content_widget import QNENodeContentWidget
from .node_socket import Socket, LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM, RIGHT_BOTTOM, RIGHT_CENTER, RIGHT_TOP
from .utils import dumpException

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node_scene import Scene

from debug.debug import return_simple_id

DEBUG = False


class Node(Serializable):
    """Implement generic node"""

    def __init__(self, scene: 'Scene', title='Undefined Node', inputs=[], outputs=[]):
        super().__init__()
        # reference to the actual scene
        self.scene = scene
        self.title = title

        self.initInnerClasses()
        self.initSettings()

        # add the node to the scene and to the graphical scene
        self.scene.addNode(self)  # basically append self to the list of nodes in Scene
        self.scene.grScene.addItem(self.grNode)  # add item to the graphical scene, so it can be displayed

        # instantiate sockets
        self.inputs = []
        self.outputs = []
        self.initSockets(inputs, outputs)

    def initInnerClasses(self):
        # Reference to the content
        self.content = QNENodeContentWidget(self)
        # Reference to the graphic
        self.grNode = QNEGraphicsNode(self)

    def initSettings(self):
        self.socket_spacing = 22
        self.input_socket_position = LEFT_BOTTOM
        self.output_socket_position = RIGHT_TOP
        self.input_multi_edged = False
        self.output_multi_edged = True

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

    # convenience function to update and get the position of the node in the graphical scene
    @property
    def pos(self):
        return self.grNode.pos()

    def setPos(self, x, y):
        self.grNode.setPos(x, y)

    @property
    def title(self, ):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        if hasattr(self, 'grNode'):
            self.grNode.title = self._title

    def getSocketPosition(self, index, position, num_out_of=1):
        """Compute the position  of the socket according to current caracteristics of the node"""
        x = 0 if position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM) else self.grNode.width
        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # start from bottom
            y = self.grNode.height - (
                    index * self.socket_spacing + self.grNode.title_vertical_padding + self.grNode.edge_roundness)
        elif position in (LEFT_CENTER, RIGHT_CENTER):
            num_sockets = num_out_of
            node_height = self.grNode.height
            top_offset = self.grNode.title_height + 2 * self.grNode.title_vertical_padding + self.grNode.edge_padding
            available_height = node_height - top_offset

            total_height_of_all_socket = num_sockets * self.socket_spacing

            new_top = available_height - total_height_of_all_socket

            # y = top_offset + index * self.socket_spacing + new_top / 2
            y = top_offset + available_height / 2. + (index - 0.5) * self.socket_spacing - \
                (num_sockets - 1) * self.socket_spacing / 2


        elif position in (LEFT_TOP, RIGHT_TOP):
            # start from top
            y = index * self.socket_spacing + self.grNode.title_height + self.grNode.title_vertical_padding + self.grNode.edge_roundness
        else:
            y = 0

        return [x, y]

    def updateConnectedEdges(self):
        for socket in self.inputs + self.outputs:
            # if socket.hasEdge():
            for edge in socket.edges:
                edge.updatePositions()

    def __str__(self):
        return return_simple_id(self, 'Node')

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

    def serialize(self):
        inputs = [socket.serialize() for socket in self.inputs]
        outputs = [socket.serialize() for socket in self.outputs]

        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('pos_x', self.grNode.scenePos().x()),
            ('pos_y', self.grNode.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs),
            ('content', self.content.serialize())
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id:
            self.id = data['id']
        hashmap[data['id']] = self

        self.setPos(data['pos_x'], data['pos_y'])
        self.title = data['title']
        # sort the sockets
        data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 1e3)
        data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 1e3)
        num_inputs = len(data['inputs'])
        num_outputs = len(data['outputs'])

        self.inputs = []
        for socket_data in data['inputs']:
            new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'],
                                socket_type=socket_data['socket_type'], count_on_this_node_side=num_inputs,
                                is_input=True)
            new_socket.deserialize(socket_data, hashmap, restore_id)
            self.inputs.append(new_socket)

        self.outputs = []
        for socket_data in data['outputs']:
            new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'],
                                socket_type=socket_data['socket_type'], count_on_this_node_side=num_outputs,
                                is_input=False)
            new_socket.deserialize(socket_data, hashmap, restore_id)
            self.outputs.append(new_socket)

        return True
