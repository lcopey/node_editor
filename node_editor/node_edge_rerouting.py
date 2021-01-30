from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node_socket import Socket
    from .node_graphics_view import NodeGraphicsView

DEBUG_REROUTING = True


class EdgeRerouting:
    def __init__(self, grView: 'NodeGraphicsView'):
        self.grView = grView
        self.routing_start_socket = None  # stores where we started re-routing the edges
        self.rerouting_edges = []  # edges representing the rerouting (dashed edges)
        self.is_rerouting = False
        self.first_mb_release = False

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
        if self.routing_start_socket is None:
            return []
        return self.routing_start_socket.edges.copy()

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
        self.routing_start_socket = None
        self.first_mb_release = False
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
        self.routing_start_socket = socket
        self.print('numEdges:', len(self.getAffectedEdges()))
        self.setAffectedEdgesVisible(False)

        start_position = self.routing_start_socket.node.getSocketScenePosition(self.routing_start_socket)

        for edge in self.getAffectedEdges():
            # get the other end of each edges affected by the rerouting
            other_socket = edge.getOtherSocket(self.routing_start_socket)

            new_edge = self.getEdgeClass()(self.routing_start_socket.node.scene, edge_type=edge.edge_type)
            new_edge.routing_start_socket = other_socket
            new_edge.grEdge.setSource(*other_socket.node.getSocketScenePosition(other_socket))
            new_edge.grEdge.setDestination(*start_position)
            new_edge.grEdge.update()

            self.rerouting_edges.append(new_edge)

    def stopRerouting(self, target: 'Socket' = None):
        self.print('stopRerouting on', target, 'no change' if target == self.routing_start_socket else '')

        if self.routing_start_socket is not None:
            # reset start socket highlight
            # TODO when is it highlighted ?
            self.routing_start_socket.grSocket.isHighLighted = False

        # collect all affected (node, edge) tuple in the meantime
        affected_nodes = []
        if target is None or target == self.routing_start_socket:
            self.setAffectedEdgesVisible(True)

        else:
            # validate edges before doing anything else
            valid_edges, invalid_edges = self.getAffectedEdges(), []
            for edge in self.getAffectedEdges():
                start_socket = edge.getOtherSocket(self.routing_start_socket)
                if not edge.validateEdge(start_socket, target):
                    # not valid edge
                    self.print('This edge rerouting is invalid', edge)
                    invalid_edges.append(edge)

            # remove the invalidated edges from the list
            for invalid_edge in invalid_edges:
                valid_edges.remove(invalid_edge)

            self.print('should reconnect from:', self.routing_start_socket, '-->', target)
            self.setAffectedEdgesVisible(True)
            for edge in valid_edges:
                for node in [edge.start_socket.node, edge.end_socket.node]:
                    if node not in affected_nodes:
                        affected_nodes.append((node, edge))

                if target.is_input:
                    target.removeAllEdges(silent=True)

                if edge.end_socket == self.routing_start_socket:
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

        self.routing_start_socket.node.scene.history.storeHistory('Rerouted edges', setModified=True)
        # reset the variables of this rerouting state
        self.resetRerouting()
