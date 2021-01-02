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

from .utils import print_func_name

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

        # custom flag used to suppress triggering onItemSelected which does a bunch of stuff
        self._silent_selection_events = False
        # flag identifying wether the current scene has been modified
        self._has_been_modified = False
        self._last_selected_items = None

        # initialize all listeners
        self._has_been_modified_listeners = []  # list of function to call when the scene is modified
        self._item_selected_listeners = []
        self._items_deselected_listeners = []

        # Store callback for retrieving the class for Nodes
        self.node_class_selector = None

        self.initUI()
        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

        self.grScene.itemSelected.connect(self.onItemSelected)
        self.grScene.itemsDeselected.connect(self.onItemsDeselected)

    def initUI(self):
        self.grScene = QNEGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)

    def getNodeByID(self, node_id: int):
        """
        Find node in the scene according to provided `node_id` (node.id).

        Parameters
        ----------
        node_id : int
            ID of the node

        Returns
        -------
        `Node` or None

        """
        for node in self.nodes:
            if node.id == node_id:
                return node

        return None

    def setSilentSelectionEvents(self, value: bool = True):
        """Calling this can suppress onItemSelected events to be triggered. This is useful when working with clipboard"""
        self._silent_selection_events = value

    def onItemSelected(self, silent=False):
        """On item selected events - store history stamp

        When the selection changed, store the current selected items and stor history stamp"""
        # if silent selection is True, ignore the event
        if self._silent_selection_events: return

        current_selected_items = self.getSelectedItems()
        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items
            if not silent:
                self.history.storeHistory('Selection Changed')
                for callback in self._item_selected_listeners:
                    callback()

    def onItemsDeselected(self, silent: bool = False):
        """Handle Items deselection and trigger event `Items Deselected`

        Call each callback in `items_deselected_listeners` and store a new history stamp

        Parameters
        ----------
        silent : bool
            if ``True`` scene's onItemsDeselected w'ont be called and history stamp not stored

        Returns
        -------

        """
        try:
            current_selected_items = self.getSelectedItems()
            if current_selected_items == self._last_selected_items:
                return

            # TODO monitor usage of this function, may be call more than once
            self.resetLastSelectedStates()
            if not current_selected_items:
                self._last_selected_items = None
                if not silent:
                    self.history.storeHistory('Deselected Everything')
                    for callback in self._items_deselected_listeners:
                        callback()
        except Exception as e:
            dumpException(e)

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

    # helper listener function
    def addHasBeenModifiedListener(self, callback: 'function'):
        """Add callabck to call everytime the scene is modified"""
        self._has_been_modified_listeners.append(callback)

    def addItemSelectedListener(self, callback: 'function'):
        self._item_selected_listeners.append(callback)

    def addItemsDeselectedListener(self, callbak: 'function'):
        self._items_deselected_listeners.append(callbak)

    def addDragEnterListener(self, callback: 'function'):
        self.getView().addDragEnterListener(callback)

    def addDropListener(self, callback: 'function'):
        self.getView().addDropListener(callback)

    # custom flag to detect node or edge has been selected
    def resetLastSelectedStates(self):
        for node in self.nodes:
            node.grNode._last_selected_state = False
        for edge in self.edges:
            edge.grEdge._last_selected_state = False

    def getEdgeClass(self):
        """Returns the class representing the Edge. Override if needed"""
        return Edge

    def getView(self):
        return self.grScene.views()[0]

    def getItemAt(self, pos):
        return self.getView().itemAt(pos)

    def getSelectedItems(self):
        return self.grScene.selectedItems()

    def doDeselectItems(self, silent: bool = False) -> None:
        """Deselects everything in scene

        Parameters
        ----------
        silent : ```bool```
            If ``True`` scene's onItemsDeselected won't be called

        Returns
        -------

        """

        for item in self.getSelectedItems():
            item.setSelected(False)
        if not silent:
            self.onItemsDeselected()

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

    def setNodeClassSelector(self, class_selecting_function):
        """When the function self.node_class_selector is set, we can use different Node classes"""
        self.node_class_selector = class_selecting_function

    def getNodeClassFromData(self, data):
        """Return corresponding Node class from data.

        Parameters
        ----------
        data : ``OrderedDict``
            as return from deserialized Node

        Returns
        -------
            Definition of Node if self.node_class_selector is not set. Else return custom defined Node class
        """
        return Node if self.node_class_selector is None else self.node_class_selector(data)

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
        try:
            # self.clear()
            # hashmap = {}
            #
            # if restore_id:
            #     self.id = data['id']
            #
            # if DEBUG: print('Deserializing nodes')
            # # create nodes
            # for node_data in data['nodes']:
            #     new_node = self.getNodeClassFromData(node_data)(self)
            #     new_node.deserialize(node_data, hashmap, restore_id)
            #
            # if DEBUG: print(' > node deserialization complete')
            #
            # # create edges
            # for edge_data in data['edges']:
            #     new_edge = Edge(self)
            #     new_edge.deserialize(edge_data, hashmap, restore_id)
            #
            # if DEBUG: print(' > edge deserialization complete')
            #
            # return True

            # get list of current nodes
            all_nodes = self.nodes.copy()

            # go through deserialized nodes
            for node_data in data['nodes']:
                # can we find this node in the scene ?
                found = False
                for node in all_nodes:
                    if node.id == node_data['id']:
                        found = node
                        break
                # Either create a new node or replace the old one
                if not found:
                    new_node = self.getNodeClassFromData(node_data)(self)
                    new_node.deserialize(node_data, hashmap, restore_id)
                    new_node.onDeserialized(node_data)
                else:
                    found.deserialize(node_data, hashmap, restore_id)
                    found.onDeserialized(node_data)
                    all_nodes.remove(found)

            # remove nodes which are left in the scene but were not in the serialized data...
            # meaning that they were not in the graph before
            while all_nodes:
                node = all_nodes.pop()
                node.remove()
                print('Scene::deserialize Removing extra nodes from scene')

            all_edges = self.edges.copy()

            for edge_data in data['edges']:
                # can we find this edge in the scene ?
                found = False
                for edge in all_edges:
                    if edge.id == edge_data['id']:
                        found = edge
                        break
                # Either create a new node or replace the old one
                if not found:
                    new_edge = Edge(self).deserialize(edge_data, hashmap, restore_id)
                else:
                    found.deserialize(edge_data, hashmap, restore_id)
                    all_edges.remove(found)

            while all_edges:
                edge = all_edges.pop()
                edge.remove()
                print('Scene::deserialize Removing extra edges from scene')

        except Exception as e:
            dumpException(e)

        return True
