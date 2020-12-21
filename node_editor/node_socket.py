from collections import OrderedDict
from .node_serializable import Serializable
from .node_graphics_socket import QNEGraphicsSocket
from debug.debug import return_simple_id

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node_node import Node

LEFT_TOP = 1
LEFT_BOTTOM = 2
RIGHT_TOP = 3
RIGHT_BOTTOM = 4


class Socket(Serializable):
    def __init__(self, node: 'Node', index=0, position=LEFT_TOP, socket_type=1):
        super().__init__()
        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type

        self.grSocket = QNEGraphicsSocket(self, self.socket_type)
        self.grSocket.setPos(*self.getSocketPosition())

        self.edge = None

    def getSocketPosition(self):
        return self.node.getSocketPosition(self.index, self.position)

    def setConnectedEdge(self, edge=None):
        self.edge = edge

    def hasEdge(self):
        return self.edge is not None

    def __str__(self):
        return return_simple_id(self, 'Socket')

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('position', self.position),
            ('socket_type', self.socket_type)
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id:
            self.id = data['id']
        hashmap[data['id']] = self
        return True
