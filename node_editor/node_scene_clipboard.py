from collections import OrderedDict
from .node_graphics_edge import QNEGraphicsEdge
from .node_node import Node
from .node_edge import Edge

DEBUG = True


class SceneClipboard:
    def __init__(self, scene):
        self.scene = scene

    def serializeSelected(self, delete=False):
        if DEBUG: print('COPY TO CLIPBOARD')
        sel_nodes, sel_edges, sel_sockets = [], [], {}

        # sort edges and nodes
        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                sel_nodes.append(item.node.serialize())
                # TODO replace by a property getting all sockets ?
                for socket in (item.node.inputs + item.node.outputs):
                    sel_sockets[socket.id] = socket
            elif isinstance(item, QNEGraphicsEdge):
                sel_edges.append(item.edge)

        # debug
        if DEBUG:
            print('  NODES\n    ', sel_nodes)
            print('  EDGES\n    ', sel_edges)
            print('  SOCKETS\n   ', sel_sockets)

        # remove all edges which are not connected to a node in our list
        # TODO simplifier !!!
        edges_to_removes = []
        for edge in sel_edges:
            if edge.start_socket.id in sel_sockets and edge.end_socket.id in sel_sockets:
                if DEBUG: print(' edge is ok, connected with both sides')

            else:
                if DEBUG: print('edge ', edge, ' is not connected with both sides')
                edges_to_removes.append(edge)

        for edge in edges_to_removes:
            sel_edges.remove(edge)

        # make final list of edges
        edges_final = []
        for edge in sel_edges:
            edges_final.append(edge.serialize())

        data = OrderedDict([
            ('nodes', sel_nodes),
            ('edges', edges_final)
        ])
        # if CUT (delete=True), remove selected items
        if delete:
            self.scene.getView().deleteSelected()
            # store our history
            self.scene.history.storeHistory('Cut out elements from scene to clipboard', setModified=True)

        return data

    def deserializeFromClipboard(self, datas):

        hashmap = {}

        # calculate mouse pointer - scene position
        view = self.scene.getView()
        mouse_scene_pos = view.last_scene_mouse_position

        # calculate selected objects bbox and center
        minx, maxx, miny, maxy = 0, 0, 0, 0
        for node_data in datas['nodes']:
            x, y = node_data['pos_x'], node_data['pos_y']
            minx = min(x, minx)
            miny = min(y, miny)
            maxx = max(x, maxx)
            maxy = max(y, maxy)

        bbox_center_x = (minx + maxx) / 2
        bbox_center_y = (miny + maxy) / 2

        # calculate the offset of the newly create nodes
        offset_x = mouse_scene_pos.x() - bbox_center_x
        offset_y = mouse_scene_pos.y() - bbox_center_y

        # create each node
        for node_data in datas['nodes']:
            new_node = self.scene.getNodeClassFromData(node_data)(self.scene)
            new_node.deserialize(node_data, hashmap, restore_id=False)
            # adjust the new node's position
            pos = new_node.pos
            new_node.setPos(pos.x() + offset_x, pos.y() + offset_y)

        # create each edge
        for edge_data in datas['edges']:
            new_edge = Edge(self.scene)
            new_edge.deserialize(edge_data, hashmap, restore_id=False)

        # store history
        self.scene.history.storeHistory('Elements pasted from the clipboard', setModified=True)
