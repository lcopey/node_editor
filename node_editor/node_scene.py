import json
from collections import OrderedDict
from .node_serializable import Serializable
from .node_graphics_scene import QNEGraphicsScene
from .node_node import Node
from .node_edge import Edge
from .node_scene_history import SceneHistory
from .node_scene_clipboard import SceneClipboard

from debug import print_func_name

DEBUG = False


class Scene(Serializable):
    """Implement the logic behind the scene being displayed.

    Contains the nodes, the edges"""

    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []
        self.scene_width = 64000
        self.scene_height = 64000
        self.grScene = None

        self._has_been_modified = False
        self._has_been_modified_listeners = []

        self.initUI()
        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

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

    def addHasBeenModifiedListener(self, callback):
        self._has_been_modified_listeners.append(callback)

    def initUI(self):
        self.grScene = QNEGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        self.nodes.remove(node)

    def removeEdge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)

    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        self.has_been_modified = False

    def saveToFile(self, filename):
        with open(filename, 'w') as file:
            serialized = self.serialize()
            file.write(json.dumps(serialized, indent=4))
            if DEBUG: print('saving to ', filename, ' was successful')

            self.has_been_modified = False

    def loadFromFile(self, filename):
        with open(filename, 'r') as file:
            raw_data = file.read()
            # data = json.loads(raw_data, encoding='utf-8')  # python 3.9 suppression de encoding
            data = json.loads(raw_data)
            self.deserialize(data)

            self.has_been_modified = False

    def serialize(self):
        nodes = [node.serialize() for node in self.nodes]
        edges = [edge.serialize() for edge in self.edges]
        return OrderedDict([('id', self.id),
                            ('scene_width', self.scene_width),
                            ('scene_height', self.scene_height),
                            ('nodes', nodes),
                            ('edges', edges)
                            ])

    def deserialize(self, data, hashmap={}, restore_id=True):
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
