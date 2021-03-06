# -*- encoding: utf-8 -*-
"""Module containing the representation of the NodeEditor's Scene"""
import json
import os
from PyQt5.QtCore import QPointF, QPoint
from collections import OrderedDict
from .utils import dumpException
from .node_serializable import Serializable
from .node_graphics_scene import GraphicsScene
from .node_node import Node
from .node_edge import Edge
from .node_scene_history import SceneHistory
from .node_scene_clipboard import SceneClipboard
from typing import TYPE_CHECKING, Union, Type

if TYPE_CHECKING:
    from .node_graphics_view import NodeGraphicsView
    from PyQt5.QtWidgets import QGraphicsItem

DEBUG = False


class InvalidFile(Exception):
    pass


class Scene(Serializable):
    """Class representing NodeEditor's Scene"""

    def __init__(self):
        """
        Instance Attributes
         - **nodes** - list of `Nodes` in thi `Scene`
         - **edges** - list of `Edges` in this `Scene`
         - **history** - Instance of :class:`~node_editor.node_scene_history.SceneHistory`
         - **clipboard** - Instance of :class:`~node_editor.node_scene_clipboard.SceneClipboard`
         - **scene_width** - `Scene` width in pixels
         - **scene_height** - `Scene` height in pixels
        """
        super().__init__()
        # init attributes
        self.grScene: Union[GraphicsScene, None] = None

        self.nodes = []
        self.edges = []
        self.scene_width = 64000
        self.scene_height = 64000

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

    @property
    def has_been_modified(self):
        """Has this `Scene` been modified

        - Setter: set new state. Triggers `Has Been Modified` event.

        Returns
        -------
        bool
            ``True`` : when the `Scene` has been modified and not saved, ``False`` otherwise

        """
        return self._has_been_modified

    def isModified(self):
        return self.has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            self._has_been_modified = value
            # call all registered listeners
            for callback in self._has_been_modified_listeners:
                callback()

        self._has_been_modified = value

    def initUI(self):
        self.grScene = GraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)

    def setSilentSelectionEvents(self, value: bool = True):
        """Calling this can suppress onItemSelected events to be triggered.
        This is useful when working with clipboard

        Parameters
        ----------
        value: bool
            if ``True``, suppress onItemSelected events,
             otherwise onItemSelected is triggered and a history stamp is stored

        Returns
        -------
        None
        """
        self._silent_selection_events = value

    def onItemSelected(self, silent: bool = False):
        """On item selected events - store history stamp

        When the selection changed, store the current selected items and store history stamp.

        Returns
        -------
        None"""
        # if silent selection is True, ignore the event
        if self._silent_selection_events:
            return

        # Detect change in selected items by comparing old selection to the new ones
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
        None
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

    # helper listener function
    def addHasBeenModifiedListener(self, callback: 'callable'):
        """Register `callback` to `Has Been Modified` event

        Parameters
        ----------
        callback : callable

        Returns
        -------
        None
        """
        self._has_been_modified_listeners.append(callback)

    def addItemSelectedListener(self, callback: 'callable'):
        """Register `callback` to `Item Selected` event

        Parameters
        ----------
        callback : callable

        Returns
        -------
        None
        """
        self._item_selected_listeners.append(callback)

    def addItemsDeselectedListener(self, callback: 'callable'):
        """Register `callback` to `Items Deselected` event

        Parameters
        ----------
        callback : callable

        Returns
        -------
        None
        """
        self._items_deselected_listeners.append(callback)

    def addDragEnterListener(self, callback: 'callable'):
        """Register `callback` to `Drag Enter` event

        Parameters
        ----------
        callback : callable

        Returns
        -------
        None
        """
        self.getView().addDragEnterListener(callback)

    def addDropListener(self, callback: 'callable'):
        """Register `callback` to `Drop` event

        Parameters
        ----------
        callback: callable

        Returns
        -------
        None
        """
        self.getView().addDropListener(callback)

    # custom flag to detect node or edge has been selected
    def resetLastSelectedStates(self):
        for node in self.nodes:
            node.grNode._last_selected_state = False
        for edge in self.edges:
            edge.grEdge._last_selected_state = False

    def getEdgeClass(self) -> Type[Edge]:
        """Returns the class representing the Edge. Override if needed

        Returns
        -------
        Type[Edge]"""
        return Edge

    def setNodeClassSelector(self, class_selecting_function: callable):
        """When the function self.node_class_selector is set, we can use different Node classes

        Parameters
        ----------
        class_selecting_function: callable
            Function returning the class of `Node` to instantiate. Used in getNodeClassFromData

        Returns
        -------
        None
        """
        self.node_class_selector = class_selecting_function

    def getNodeClassFromData(self, data: OrderedDict):
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

    def getView(self) -> 'NodeGraphicsView':
        """Returns current NodeGraphicsView instance.

        Returns
        -------
        NodeGraphicsView
        """
        return self.grScene.views()[0]

    def getItemAt(self, pos: Union[QPoint, QPointF]) -> 'QGraphicsItem':
        """Returns the QGraphicsItem at position in the current graphics view

        Parameters
        ----------
        pos: Union[QPoint, QPointF]
            position in the view

        Returns
        -------
        QGraphicsItem
        """
        if isinstance(pos, QPointF):
            pos = QPoint(pos.x(), pos.y())
        return self.getView().itemAt(pos)

    def getSelectedItems(self):
        return self.grScene.selectedItems()

    def getLastSelectedItems(self):
        return self._last_selected_items

    def getNodeByID(self, node_id: int) -> Union[Node, None]:
        """Find node in the scene according to provided `node_id` (node.id).

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

    def doDeselectItems(self, silent: bool = False) -> None:
        """Deselects everything in scene

        Parameters
        ----------
        silent : ``bool``
            If ``True`` scene's onItemsDeselected won't be called

        Returns
        -------
        None
        """
        for item in self.getSelectedItems():
            item.setSelected(False)
        if not silent:
            self.onItemsDeselected()

    def addNode(self, node: Node):
        """Append node to the list of nodes"""
        self.nodes.append(node)

    def addEdge(self, edge: Edge):
        """Append edge to the list of edges"""
        self.edges.append(edge)

    def removeNode(self, node: Node):
        """Remove node from the list of nodes"""
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            print('!W', 'Scene:removeNode', 'wanna remove edge', node, 'from self.nodes but it is not in the list!')

    def removeEdge(self, edge: Edge):
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

    def saveToFile(self, filename: str):
        """Save current graph to filename.

        Parameters
        ----------
        filename: str

        Returns
        -------
        None
        """
        with open(filename, 'w') as file:
            serialized = self.serialize()
            file.write(json.dumps(serialized, indent=4))
            self.print('saving to ', filename, ' was successful')

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
        self.print("Scene holding {} items".format(len(self.grScene.items())))
        nodes = [node.serialize() for node in self.nodes]
        edges = [edge.serialize() for edge in self.edges]
        return OrderedDict([('id', self.id),
                            ('scene_width', self.scene_width),
                            ('scene_height', self.scene_height),
                            ('nodes', nodes),
                            ('edges', edges)
                            ])

    def deserialize(self, data: dict, hashmap: Union[dict, None] = None, restore_id: bool = True) -> bool:
        hashmap = {}
        if restore_id:
            self.id = data['id']
        try:
            # get list of current nodes
            all_nodes = self.nodes.copy()

            # go through deserialized nodes
            for node_data in data['nodes']:
                # can we find this node in the scene ?
                found: Union[Node, bool] = False
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

            print("Scene holding {} items".format(len(self.grScene.items())))

        except Exception as e:
            dumpException(e)

        return True

    def print(self, *args):
        if DEBUG:
            print('>Scene :', *args)
