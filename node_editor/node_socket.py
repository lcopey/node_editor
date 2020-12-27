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
    def __init__(self, node: 'Node', index=0, position=LEFT_TOP, socket_type=1, multi_edges=True):
        super().__init__()
        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.is_multi_edges = multi_edges

        self.grSocket = QNEGraphicsSocket(self, self.socket_type)
        self.grSocket.setPos(*self.getSocketPosition())

        self.edges = []

    def getSocketPosition(self):
        return self.node.getSocketPosition(self.index, self.position)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeEdge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            print('!W', 'Socket:removeEdge', 'wanna remove edge', edge, 'from self.edges but it is not in the list!')

    def removeAllEdges(self):
        while self.edges:
            edge = self.edges.pop(0)
            edge.remove()
        # self.edges.clear()

    # def hasEdge(self):
    #     return self.edges is not None

    def __str__(self):
        return return_simple_id(self, 'Socket')

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('multi_edges', self.is_multi_edges),
            ('position', self.position),
            ('socket_type', self.socket_type),
        ])

    def determineMultiedges(self, data):
        if 'multi_edges' in data:
            return data['multi_edges']
        else:
            # probably older versions of file
            return data['position'] in (RIGHT_BOTTOM, RIGHT_TOP)

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id:
            self.id = data['id']
        self.is_multi_edges = self.determineMultiedges(data)
        hashmap[data['id']] = self
        return True
