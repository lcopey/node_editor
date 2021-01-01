from collections import OrderedDict
from .node_serializable import Serializable
from debug.debug import return_simple_id
from .node_graphics_edge import *

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2

DEBUG = False

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .node_scene import Scene
    from .node_socket import Socket


class Edge(Serializable):
    def __init__(self, scene: Optional['Scene'] = None, start_socket: Optional['Socket'] = None,
                 end_socket: Optional['Socket'] = None,
                 edge_type=EDGE_TYPE_DIRECT):
        super().__init__()
        self.scene = scene
        # default init
        self._start_socket = None
        self._end_socket = None

        self.start_socket = start_socket
        self.end_socket = end_socket
        self.edge_type = edge_type

        self.scene.addEdge(self)

    # properties and setters
    @property
    def start_socket(self):
        return self._start_socket

    @start_socket.setter
    def start_socket(self, value):
        # If we wer assigne to some socket before, delte us from the socket
        if self._start_socket is not None:
            self._start_socket.removeEdge(self)

        # assign new start socket
        self._start_socket = value
        # addEdge to the Socket class
        if self.start_socket is not None:
            self.start_socket.addEdge(self)

    @property
    def end_socket(self):
        return self._end_socket

    @end_socket.setter
    def end_socket(self, value):
        # If we wer assigne to some socket before, delte us from the socket
        if self._end_socket is not None:
            self._end_socket.removeEdge(self)

        # assign new end socket
        self._end_socket = value
        # addEdge to the Socket class
        if self.end_socket is not None:
            self.end_socket.addEdge(self)

    @property
    def edge_type(self):
        return self._edge_type

    @edge_type.setter
    def edge_type(self, value):
        """Setter for the edge type.

        In case of change, the graphical edge is automatically set to the corresponding edge type."""
        if hasattr(self, 'grEdge') and self.grEdge is not None:
            self.scene.grScene.removeItem(self.grEdge)
        self._edge_type = value
        if self.edge_type == EDGE_TYPE_DIRECT:
            self.grEdge = QNEGraphicsEdgeDirect(self)
        elif self.edge_type == EDGE_TYPE_BEZIER:
            self.grEdge = QNEGraphicsEdgeBezier(self)
        else:
            self.grEdge = QNEGraphicsEdgeBezier(self)

        self.scene.grScene.addItem(self.grEdge)
        if self.start_socket is not None:
            self.updatePositions()

    def getOtherSocket(self, known_socket):
        # return the other end of the edge
        return self.start_socket if known_socket == self.end_socket else self.end_socket

    def updatePositions(self):
        source_pos = self.start_socket.getSocketPosition()
        source_pos[0] += self.start_socket.node.grNode.pos().x()
        source_pos[1] += self.start_socket.node.grNode.pos().y()
        self.grEdge.setSource(*source_pos)

        if self.end_socket is not None:
            end_pos = self.end_socket.getSocketPosition()
            end_pos[0] += self.end_socket.node.grNode.pos().x()
            end_pos[1] += self.end_socket.node.grNode.pos().y()
            self.grEdge.setDestination(*end_pos)
        else:
            self.grEdge.setDestination(*source_pos)

        self.grEdge.update()

    def remove_from_sockets(self):
        """Remove the edges from the sockets

        - Remove  the reference of the edge in the sockets.
        - Start socket and end socket are assigned to None"""
        # # TODO Fix Me!!!!
        # if self.start_socket is not None:
        #     self.start_socket.removeEdge(None)
        #
        # if self.end_socket is not None:
        #     self.end_socket.removeEdge(None)

        self.end_socket = None
        self.start_socket = None

    def remove(self):
        if DEBUG: print("> Removing Edge")
        if DEBUG: print(" - remove edge from all sockets")
        self.remove_from_sockets()
        if DEBUG: print(" - remove grEdge")
        self.scene.grScene.removeItem(self.grEdge)
        self.grEdge = None
        if DEBUG: print(" - remove edge from scene")
        self.scene.removeEdge(self)
        if DEBUG: print(" - everything was done")

    def __str__(self):
        return return_simple_id(self, 'Edge')

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('edge_type', self.edge_type),
            ('start', self.start_socket.id),
            ('end', self.end_socket.id)
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id:
            self.id = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.edge_type = data['edge_type']
