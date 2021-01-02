from collections import OrderedDict
from .node_serializable import Serializable
from .node_graphics_socket import QNEGraphicsSocket
from .utils import return_simple_id

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node_node import Node

LEFT_TOP = 1
LEFT_CENTER = 2
LEFT_BOTTOM = 3
RIGHT_TOP = 4
RIGHT_CENTER = 5
RIGHT_BOTTOM = 6


class Socket(Serializable):
    Socket_GR_Class = QNEGraphicsSocket

    """Class representing Socket"""

    def __init__(self, node: 'Node', index=0, position=LEFT_TOP, socket_type=1, multi_edges=True,
                 count_on_this_node_side=1, is_input=False):
        super().__init__()
        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.is_multi_edges = multi_edges
        self.count_on_this_node_side = count_on_this_node_side
        self.is_input = is_input
        self.is_output = not self.is_input

        self.grSocket = self.__class__.Socket_GR_Class(self)
        self.setSocketPosition()

        self.edges = []

    def __str__(self):
        return return_simple_id(self, 'Socket')

    def delete(self):
        """Delete this ``Socket`` from graphics scene"""
        self.grSocket.setParentItem(None)
        self.node.scene.grScene.removeItem(self.grSocket)
        del self.grSocket

    def changeSocketType(self, new_socket_type: int):
        if self.socket_type != new_socket_type:
            self.socket_type = new_socket_type
            self.grSocket.changeSocketType()

    def setSocketPosition(self):
        self.grSocket.setPos(*self.node.getSocketPosition(self.index, self.position, self.count_on_this_node_side))

    def getSocketPosition(self):
        return self.node.getSocketPosition(self.index, self.position, self.count_on_this_node_side)

    def hasAnyEdge(self) -> bool:
        return len(self.edges) > 0

    def isConnected(self, edge: 'Edge') -> bool:
        return edge in self.edges

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeEdge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            print('!W', 'Socket:removeEdge', 'wanna remove edge', edge, 'from self.edges but it is not in the list!')

    def removeAllEdges(self, silent=False):
        while self.edges:
            edge = self.edges.pop(0)
            if silent:
                edge.remove(silent_for_socket=self)
            else:
                edge.remove()

    def determineMultiedges(self, data):
        if 'multi_edges' in data:
            return data['multi_edges']
        else:
            # probably older versions of file
            return data['position'] in (RIGHT_BOTTOM, RIGHT_TOP)

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('multi_edges', self.is_multi_edges),
            ('position', self.position),
            ('socket_type', self.socket_type),
        ])

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True):
        if restore_id:
            self.id = data['id']
        self.is_multi_edges = self.determineMultiedges(data)
        hashmap[data['id']] = self
        return True
