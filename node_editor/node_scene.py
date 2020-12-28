import json
import os
from collections import OrderedDict
from .utils import dumpException
from .node_serializable import Serializable
from .node_graphics_scene import QNEGraphicsScene
from .node_node import Node
from .node_edge import Edge
from .node_scene_history import SceneHistory
from .node_scene_clipboard import SceneClipboard

from debug import print_func_name

DEBUG = False


class InvalidFile(Exception): pass


class Scene(Serializable):
    """Implement the logic behind the scene being displayed.

    Contains the nodes, the edges"""

    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []
        self.scene_width = 64000
        self.scene_height = 64000
        # self.grScene = None

        self._has_been_modified = False  # flag identifying wether the current scene has been modified
        self._has_been_modified_listeners = []  # list of function to call when the scene is modified

        self.initUI()
        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

    def isModified(self):
        return self.has_been_modified

    @property
    def has_been_modified(self):
        return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            self._has_been_modified = value
            # call all registered listeners
            for callback in self._has_been_modified_listeners:
                callback()

        self._has_been_modified = value

    def addHasBeenModifiedListener(self, callback: 'function'):
        """Add callabck to call everytime the scene is modified"""
        self._has_been_modified_listeners.append(callback)

    def getSelectedItems(self):
        return self.grScene.selectedItems()

    def initUI(self):
        self.grScene = QNEGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)

    def addNode(self, node):
        """Append node to the list of nodes"""
        self.nodes.append(node)

    def addEdge(self, edge):
        """Append edge to the list of edges"""
        self.edges.append(edge)

    def removeNode(self, node):
        """Remove node from the list of nodes"""
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            print('!W', 'Scene:removeNode', 'wanna remove edge', node, 'from self.nodes but it is not in the list!')

    def removeEdge(self, edge):
        """Remove edge from the list of edges"""
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            print('!W', 'Scene:removeEdge', 'wanna remove edge', edge, 'from self.edges but it is not in the list!')

    def clear(self):
        """Clear the scene by calling remove() on all the nodes"""
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        self.has_been_modified = False

    def saveToFile(self, filename):
        """Save current graph to filename"""
        with open(filename, 'w') as file:
            serialized = self.serialize()
            file.write(json.dumps(serialized, indent=4))
            if DEBUG: print('saving to ', filename, ' was successful')

            self.has_been_modified = False

    def loadFromFile(self, filename):
        """Load graph from filename"""
        with open(filename, 'r') as file:
            raw_data = file.read()
            # data = json.loads(raw_data, encoding='utf-8')  # python 3.9 suppression de encoding
            try:
                data = json.loads(raw_data)
                self.deserialize(data)
                self.has_been_modified = False
            except json.JSONDecodeError:
                raise InvalidFile(f'{os.path.basename(filename)} is not a valid JSON file')
            except Exception as e:
                dumpException(e)

    def serialize(self):
        """Serialize the scene.

        Call serialize from each object, nodes and edges. Following parameters are serialized :
            - scene width
            - scene height
            - nodes
            - edges
        """
        nodes = [node.serialize() for node in self.nodes]
        edges = [edge.serialize() for edge in self.edges]
        return OrderedDict([('id', self.id),
                            ('scene_width', self.scene_width),
                            ('scene_height', self.scene_height),
                            ('nodes', nodes),
                            ('edges', edges)
                            ])

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        """Deserialize the scene by recursively calling deserialize function on each node and edges.

        Parameters
        ----------
        data : dict
        hashmap : dict
        restore_id : bool default True

        Returns
        -------
        bool
            - True if deserialize is successful

        """
        self.clear()
        hashmap = {}

        if restore_id:
            self.id = data['id']

        if DEBUG: print('Deserializing nodes')
        # create nodes
        for node_data in data['nodes']:
            new_node = Node(self)
            new_node.deserialize(node_data, hashmap, restore_id)

        if DEBUG: print(' > node deserialization complete')

        # create edges
        for edge_data in data['edges']:
            new_edge = Edge(self)
            new_edge.deserialize(edge_data, hashmap, restore_id)

        if DEBUG: print(' > edge deserialization complete')

        return True
