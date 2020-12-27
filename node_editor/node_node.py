from collections import OrderedDict
from .node_serializable import Serializable
from .node_graphics_node import QNEGraphicsNode
from .widgets.node_content_widget import QNENodeContentWidget
from .node_socket import Socket, LEFT_TOP, LEFT_BOTTOM, RIGHT_BOTTOM, RIGHT_TOP
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
        self.content = QNENodeContentWidget(self)
        # reference to the graphic
        self.grNode = QNEGraphicsNode(self)

        # add the node to the scene and to the graphical scene
        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

        self.socket_spacing = 22

        # instantiate sockets
        self.inputs = []
        self.outputs = []
        for n, item in enumerate(inputs):
            socket = Socket(node=self, index=n, position=LEFT_BOTTOM, socket_type=item, multi_edges=False)
            self.inputs.append(socket)

        for n, item in enumerate(outputs):
            socket = Socket(node=self, index=n, position=RIGHT_TOP, socket_type=item, multi_edges=True)
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

    def getSocketPosition(self, index, position):
        x = 0 if position in (LEFT_TOP, LEFT_BOTTOM) else self.grNode.width
        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # start from bottom
            y = self.grNode.height - (index * self.socket_spacing + self.grNode.title_height + self.grNode.edge_size)
        else:
            # start from top
            y = index * self.socket_spacing + self.grNode.title_height + self.grNode.edge_size

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

        self.inputs = []
        for socket_data in data['inputs']:
            new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'],
                                socket_type=socket_data['socket_type'], )
            new_socket.deserialize(socket_data, hashmap, restore_id)
            self.inputs.append(new_socket)

        self.outputs = []
        for socket_data in data['outputs']:
            new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'],
                                socket_type=socket_data['socket_type'])
            new_socket.deserialize(socket_data, hashmap, restore_id)
            self.outputs.append(new_socket)

        return True
