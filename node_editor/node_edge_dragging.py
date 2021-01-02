from PyQt5.QtWidgets import QGraphicsView
from .node_edge import EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT, Edge
from .node_graphics_socket import QNEGraphicsSocket
from .utils import print_items, dumpException

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .node_graphics_view import QNEGraphicsView

DEBUG = False


class EdgeDragging:
    def __init__(self, grView: 'QNEGraphicsView'):
        self.grView = grView

    def getEdgeClass(self):
        """Helper function to get the Edge class. Using what SCene class provides"""
        return self.grView.grScene.scene.getEdgeClass()

    def updateDestination(self, x: float, y: float):
        """Update the end point of our dragging edge

        Parameters
        ----------
        x : float
            x position of the end `Socket` in the `Scene`
        y : float
            y position of the end `Socket` in the `Scene`

        Returns
        -------

        """
        if self.drag_edge is not None and self.drag_edge.grEdge is not None:
            self.drag_edge.grEdge.setDestination(x, y)
            self.drag_edge.grEdge.update()
        else:
            print("View::mouseMoveEvent Trying to update drag_edge/grEdge but None")

    def edgeDragStart(self, item):
        """Start the dragging of a dashed `Edge`

        `drag_start_socket` and `drag_edge` are created here as references to the current socket and the edge in the
         dragging event.

        Parameters
        ----------
        item : QNEGraphicsSocket
            grSocket where the click initiated the dragging mode

        """
        try:
            if DEBUG:
                print('Clicked :')
                print_items(item)

            # Store previous edge and socket if existing
            self.drag_start_socket = item.socket

            # Create a new edge
            self.drag_edge = self.getEdgeClass()(item.socket.node.scene, item.socket, None, EDGE_TYPE_BEZIER)
            if DEBUG:
                print('Dragging :')
                print_items(self.drag_edge.grEdge)
        except Exception as e:
            dumpException(e)

    def edgeDragEnd(self, item):
        """Return True if skip the rest of the code"""

        self.grView.resetMode()
        if DEBUG: print('View:edgeDragEnd - End dragging edge')
        # remove the edge without trigerring any event
        self.drag_edge.remove(silent=True)
        self.drag_edge = None

        try:
            if isinstance(item, QNEGraphicsSocket) and item.socket is not self.drag_start_socket:
                # if we released dragging on a socket (other than beginning socket)
                # if not multi_edges, remove all edges from the existing socket
                for socket in (item.socket, self.drag_start_socket):
                    if not socket.is_multi_edges:
                        if socket.is_input:
                            socket.removeAllEdges(silent=True)
                        else:
                            socket.removeAllEdges(silent=False)
                # if not item.socket.is_multi_edges:
                #     item.socket.removeAllEdges()
                # if not self.drag_start_socket.is_multi_edges:
                #     self.drag_start_socket.removeAllEdges()

                # Creating new edge
                # the edge is automatically added to the scene and the corresponding socket
                new_edge = self.getEdgeClass()(item.socket.node.scene, self.drag_start_socket, item.socket,
                                               edge_type=EDGE_TYPE_BEZIER)

                if DEBUG: print('View:edgeDragEnd - Created new edge', new_edge, 'connecting', new_edge.start_socket,
                                '<-->', new_edge.end_socket)

                for socket in [self.drag_start_socket, item.socket]:
                    socket.node.onEdgeConnectionChanged(new_edge)
                    if socket.is_input:
                        socket.node.onInputChanged(socket)

                self.grView.scene.history.storeHistory('Created new edge by dragging', setModified=True)

                return True
        except Exception as e:
            dumpException(e)

        if DEBUG: print('View:edgeDragEnd - everything done')

        return False
