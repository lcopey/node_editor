from collections import OrderedDict
from .node_graphics_edge import GraphicsEdge
from .node_node import Node
from .node_edge import Edge

DEBUG = False
DEBUG_PASTING = False


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
                for socket in item.node.getSockets():
                    sel_sockets[socket.id] = socket
            elif isinstance(item, GraphicsEdge):
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

    def deserializeFromClipboard(self, datas: dict):

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

        # add width and height of a node
        maxx -= 180
        maxy += 100

        relbboxcenterx = (minx + maxx) / 2
        relbboxcentery = (miny + maxy) / 2

        # calculate the offset of the newly create nodes
        mousex, mousey = mouse_scene_pos.x(), mouse_scene_pos.y()

        if DEBUG_PASTING:
            print(" *** PASTA:")
            print("Copied boudaries:\n\tX:", minx, maxx, "   Y:", miny, maxy)
            print("\tbbox_center:", relbboxcenterx, relbboxcentery)

        created_nodes = []
        self.scene.setSilentSelectionEvents()

        self.scene.doDeselectItems()

        # create each node
        for node_data in datas['nodes']:
            new_node = self.scene.getNodeClassFromData(node_data)(self.scene)
            new_node.deserialize(node_data, hashmap, restore_id=False)
            created_nodes.append(new_node)

            # adjust the new node's position
            posx, posy = new_node.pos.x(), new_node.pos.y()
            newx, newy = mousex + posx - minx, mousey + posy - miny
            new_node.setPos(newx, newy)

            # do not trigger event as setSilentSelectionEvents was called
            new_node.doSelect()

            if DEBUG_PASTING:
                print("** PASTA SUM:")
                print("\tMouse pos:", mousex, mousey)
                print("\tnew node pos:", posx, posy)
                print("\tFINAL:", newx, newy)

        # create each edge
        for edge_data in datas['edges']:
            new_edge = Edge(self.scene)
            new_edge.deserialize(edge_data, hashmap, restore_id=False)

        self.scene.setSilentSelectionEvents(False)

        # store history
        self.scene.history.storeHistory('Elements pasted from the clipboard', setModified=True)

        return created_nodes
