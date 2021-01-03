from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node_socket import Socket
    from .node_graphics_view import QNEGraphicsView

DEBUG_REROUTING = True


class EdgeRerouting:
    def __init__(self, grView: 'QNEGraphicsView'):
        self.grView = grView
        self.start_socket = None  # stores where we started re-routing the edges
        self.rerouting_edges = []  # edges representing the rerouting (dashed edges)
        self.is_rerouting = False

    def print(self, *args):
        if DEBUG_REROUTING: print('Rerouting: ', *args)

    def getEdgeClass(self):
        return self.grView.scene.getEdgeClass()

    def getAffectedEdges(self) -> list:
        """Returns the `Edges` connected on `start_socket`

        Returns
        -------
        list
            list of `Edges` connected to `start_socket`

        """
        if self.start_socket is None:
            return []
        return self.start_socket.edges.copy()

    def setAffectedEdgesVisible(self, visibility=True):
        """Change the visibility of `Graphical Edges` connected to `start_socket`

        Parameters
        ----------
        visibility : bool
            ``True`` : `Graphical Edges` connected to `start_socket` are visible
            ``False`` : `Graphical Edges` connected to `start_socket` are hidden
        """
        for edge in self.getAffectedEdges():
            if visibility:
                edge.grEdge.show()
            else:
                edge.grEdge.hide()
        self.print('setVisibility to', visibility)
    def resetRerouting(self):
        self.is_rerouting = False
        self.start_socket = None
        # all rerouting edges should be empty at this point
        # self.rerouting_edges = []

    def clearReroutingEdges(self):
        self.print('clean called')
        while self.rerouting_edges:
            edge = self.rerouting_edges.pop()
            self.print('want to clean ', edge)
            edge.remove()

    def updateScenePos(self, x, y):
        if self.is_rerouting:
            for edge in self.rerouting_edges:
                if edge and edge.grEdge:
                    edge.grEdge.setDestination(x, y)
                    edge.grEdge.update()


    def startRerouting(self, socket: 'Socket' = None):
        self.print('StartRerouting on', socket)
        self.is_rerouting = True
        self.start_socket = socket
        self.print('numEdges:', len(self.getAffectedEdges()))
        self.setAffectedEdgesVisible(False)

        start_position = self.start_socket.node.getSocketScenePosition(self.start_socket)

        for edge in self.getAffectedEdges():
            # get the other end of each edges affected by the rerouting
            other_socket = edge.getOtherSocket(self.start_socket)
            new_edge = self.getEdgeClass()(self.start_socket.node.scene, edge_type=edge.edge_type)
            new_edge.start_socket = other_socket
            new_edge.grEdge.setSource(*other_socket.node.getSocketScenePosition(other_socket))
            new_edge.grEdge.setDestination(*start_position)
            new_edge.grEdge.update()

            self.rerouting_edges.append(new_edge)

    def stopRerouting(self, target: 'Socket' = None):
        self.print('stopRerouting on', target, 'no change' if target == self.start_socket else '')

        if self.start_socket is not None:
            # reset start socket highlight
            self.start_socket.grSocket.isHighLighted = False

        # collect all affected (node, edge) tuple in the meantime
        affected_nodes = []
        if target is None or target == self.start_socket:
            self.setAffectedEdgesVisible(True)

        else:
            self.print('should reconnect from:', self.start_socket, '-->', target)
            self.setAffectedEdgesVisible(True)
            for edge in self.getAffectedEdges():
                for node in [edge.start_socket.node, edge.end_socket.node]:
                    if node not in affected_nodes:
                        affected_nodes.append((node, edge))

                if target.is_input:
                    target.removeAllEdges(silent=True)

                if edge.end_socket == self.start_socket:
                    edge.end_socket = target
                else:
                    edge.start_socket = target

                edge.updatePositions()


        # hide rerouting edges
        self.clearReroutingEdges()

        # send notifications for all affected nodes
        for affected_node, edge in affected_nodes:
            affected_node.onEdgeConnectionChanged(edge)
            if edge.start_socket in affected_node.inputs:
                affected_node.onInputChanged(edge.start_socket)
            if edge.end_socket in affected_node.inputs:
                affected_node.onInputChanged(edge.end_socket)

        self.start_socket.node.scene.history.storeHistory('Rerouted edges', setModified=True)
        # reset the variables of this rerouting state
        self.resetRerouting()

