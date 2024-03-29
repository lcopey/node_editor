from PyQt5.QtWidgets import QGraphicsView
from .node_edge import EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT, Edge
from .node_graphics_socket import GraphicsSocket
from .utils import print_items, dumpException

from typing import TYPE_CHECKING, Union, Type

if TYPE_CHECKING:
    from .node_graphics_view import NodeGraphicsView
    from .node_socket import Socket

DEBUG = False


class EdgeDragging:
    def __init__(self, view: 'NodeGraphicsView'):
        self.grView = view
        self.drag_start_socket: Union['Socket', None] = None
        self.drag_edge: Union[Edge, None] = None

    def getEdgeClass(self) -> Type[Edge]:
        """Helper function to get the Edge class. Using what SCene class provides"""
        return self.grView.scene.getEdgeClass()

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

    def edgeDragStart(self, item: 'GraphicsSocket'):
        """Start the dragging of a dashed `Edge`

        `drag_start_socket` and `drag_edge` are created here as references to the current socket and the edge in the
         dragging event.

        Parameters
        ----------
        item : GraphicsSocket
            grSocket where the click initiated the dragging mode

        """
        try:
            self.print('Clicked :', item)

            # Store previous edge and socket if existing
            self.drag_start_socket = item.socket

            # Create a new edge
            self.drag_edge = self.getEdgeClass()(item.socket.node.scene, item.socket, None, EDGE_TYPE_BEZIER)
            self.print('Dragging :', self.drag_edge.grEdge)

        except Exception as e:
            dumpException(e)

    def edgeDragEnd(self, item) -> bool:
        """End the dragging of a dashed `Edge`.

        Triggers Nodes':

        - :py:meth:`~node_editor.node_node.Node.onEdgeConnectionChanged`
        - :py:meth:`~node_editor.node_node.Node.onInputChanged`

        Parameters
        ----------
        item : GraphicsSocket
            Item in the `Graphics Scene` where we ended dragging an `Edge`

        Returns
        -------
        bool
            True if a new Edge was successfully created
            False otherwise

        """
        try:
            if not isinstance(item, GraphicsSocket):
                self.grView.resetMode()
                self.print('View:edgeDragEnd - End dragging edge')
                # remove the edge without trigerring any event
                self.drag_edge.remove(silent=True)
                self.drag_edge = None

            if isinstance(item, GraphicsSocket) and item.socket is not self.drag_start_socket:

                # check if edge would be valid
                if not self.drag_edge.validateEdge(self.drag_start_socket, item.socket):
                    print("NOT VALID EDGE")
                    return False

                # if we released dragging on a socket (other than beginning socket)
                # if not multi_edges, remove all edges from the existing socket
                self.grView.resetMode()

                # remove the edge without trigerring any event
                self.drag_edge.remove(silent=True)
                self.drag_edge = None

                for socket in (item.socket, self.drag_start_socket):
                    if not socket.is_multi_edges:
                        if socket.is_input:
                            socket.removeAllEdges(silent=True)
                        else:
                            socket.removeAllEdges(silent=False)

                # Creating new edge
                # the edge is automatically added to the scene and the corresponding socket
                new_edge = self.getEdgeClass()(item.socket.node.scene, self.drag_start_socket, item.socket,
                                               edge_type=EDGE_TYPE_BEZIER)

                self.print('View:edgeDragEnd - Created new edge', new_edge, 'connecting', new_edge.start_socket,
                           '<-->', new_edge.end_socket)

                for socket in [self.drag_start_socket, item.socket]:
                    # Notify Edge Connection Changed
                    socket.node.onEdgeConnectionChanged(new_edge)
                    if socket.is_input:
                        socket.node.onInputChanged(socket)

                self.grView.scene.history.storeHistory('Created new edge by dragging', setModified=True)

                return True
        except Exception as e:
            dumpException(e)

        if DEBUG: print('View:edgeDragEnd - everything done')

        return False

    def print(self, *args):
        if DEBUG:
            print('>Edge dragging :', *args)
