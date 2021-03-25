# -*- encoding: utf-8 *-*
from collections import OrderedDict
from .node_serializable import Serializable
from .utils import return_simple_id, dumpException
from .node_graphics_edge import *

from typing import TYPE_CHECKING, Optional, Type

if TYPE_CHECKING:
    from .node_scene import Scene
    from .node_socket import Socket

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2

DEBUG = False


class Edge(Serializable):
    """Class for representing `Edge`"""
    edge_validators = []  #: class variable containing list of registered edge validators

    def __init__(self, scene: Optional['Scene'] = None, start_socket: Optional['Socket'] = None,
                 end_socket: Optional['Socket'] = None,
                 edge_type: int = EDGE_TYPE_DIRECT):
        """Instantiates a `Edge` object holding the logic to create a new edge, the edge type (Bezier or direct) and
        which :class:`~node_editor.node_scene.Socket` it can connect to.

        **Instance Attributes**

        - scene : Reference to the :class:`~node_editor.node_scene.Scene`
        - grEdge : Reference to the :class:`~node_editor.node_graphics_edge.GraphicsEdge`

        Parameters
        ----------
        scene: Optional[`Scene`]
            Reference to :class:`~node_editor.node_scene.Scene`
        start_socket: Optional[`Socket`]
            Reference to first :class:`~node_editor.node_scene.Socket`
        end_socket: Optional[`Socket`]
            Reference to last :class:`~node_editor.node_scene.Socket`
        edge_type: int
            One of EDGE_TYPE_DIRECT or EDGE_TYPE_BEZIER
        """
        super().__init__()
        self.scene = scene
        # default init
        self._start_socket = None
        self._end_socket = None

        self.start_socket = start_socket
        self.end_socket = end_socket
        self._edge_type = edge_type

        # create Graphics Edge
        self.grEdge = self.createEdgeClassInstance()

        self.scene.addEdge(self)

    def __str__(self):
        return return_simple_id(self, 'Edge')

    # properties and setters
    @property
    def start_socket(self):
        return self._start_socket

    @start_socket.setter
    def start_socket(self, value):
        # If we wer assigne to some socket before, delte us from the socket
        if self._start_socket is not None:
            self._start_socket.removeEdge(self)

        # assign new start socket
        self._start_socket = value
        # addEdge to the Socket class
        if self.start_socket is not None:
            self.start_socket.addEdge(self)

    @property
    def end_socket(self):
        return self._end_socket

    @end_socket.setter
    def end_socket(self, value):
        # If we were assigne to some socket before, delte us from the socket
        if self._end_socket is not None:
            self._end_socket.removeEdge(self)

        # assign new end socket
        self._end_socket = value
        # addEdge to the Socket class
        if self.end_socket is not None:
            self.end_socket.addEdge(self)

    @property
    def edge_type(self):
        return self._edge_type

    @edge_type.setter
    def edge_type(self, value: int):
        """Setter for the edge type.

        In case of change, the graphical edge is automatically set to the corresponding edge type.
        Parameters
        ----------
        value: int
            One of EDGE_TYPE_DIRECT or EDGE_TYPE_BEZIER

        Returns
        -------
        None
        """
        # if hasattr(self, 'grEdge') and self.grEdge is not None:
        #     self.scene.grScene.removeItem(self.grEdge)
        self._edge_type = value
        self.grEdge.createEdgePathCalculator()

        if self.start_socket is not None:
            self.updatePositions()

    def getGraphicsEdgeClass(self) -> Type[GraphicsEdge]:
        """Returns the class representing the Graphics Edge. Override if needed"""
        return GraphicsEdge

    def createEdgeClassInstance(self) -> GraphicsEdge:
        """Create instance of grEdge class

        Override if needed
        Returns
        -------
        GraphicsEdge
            Instance of grEdge class representing the :class:`~node_editor.node_graphics_edge.GraphicsEdge`
        """
        self.grEdge: GraphicsEdge = self.getGraphicsEdgeClass()(self)
        self.scene.grScene.addItem(self.grEdge)
        if self.start_socket is not None:
            self.updatePositions()
        return self.grEdge

    @classmethod
    def getEdgeValidators(cls):
        """Return the list of Edge Validator Callbacks"""
        return cls.edge_validators

    @classmethod
    def registerEdgeValidator(cls, validator_callback: 'callable'):
        """Register Edge Validator Callback

        Parameters
        ----------
        validator_callback : 'callable'
            A function handle to validate Edge
        Returns
        -------
        None
        """
        cls.edge_validators.append(validator_callback)

    @classmethod
    def validateEdge(cls, start_socket: 'Socket', end_socket: 'Socket') -> bool:
        """Validate Edge agains all registered `Edge Validator Callbacks`

        Parameters
        ----------
        start_socket : :class:`~nodeeditor.node_socket.Socket`
            Starting :class:`~nodeeditor.node_socket.Socket` of Edge to check

        end_socket : :class:`~nodeeditor.node_socket.Socket`
            Target/End :class:`~nodeeditor.node_socket.Socket` of Edge to check

        Returns
        -------
        ``bool``
            ``True`` if the Edge is valid or ``False`` if not
        """
        for validator in cls.getEdgeValidators():
            if not validator(start_socket, end_socket):
                return False
        return True

    def getOtherSocket(self, known_socket: 'Socket') -> 'Socket':
        """Returns the opposite socket on this `Edge`

        Parameters
        ----------
        known_socket: Socket
            First side of :class:`~node_editor.node_socket.Socket`

        Returns
        -------
        `Socket`
            Returns the opposite socket on this :class:`~node_editor.node_edge.Edge`
        """
        # return the other end of the edge
        return self.start_socket if known_socket == self.end_socket else self.end_socket

    def doSelect(self, new_state: bool = True):
        """Select or deselect of the Edge.

        Triggers the onSelected event that store a new historty stamp
        Parameters
        ----------
        new_state : ``bool``
            ``True`` for selected, ``False`` for unselected
        """
        self.grEdge.doSelect(new_state)

    def updatePositions(self):
        """Updates the internal `Graphics Edge` positions according to the start and end
        :class:`~node_editor.node_socket.Socket`.
        This should be called if you update ``Edge`` positions."""
        source_pos = self.start_socket.getSocketPosition()
        source_pos[0] += self.start_socket.node.grNode.pos().x()
        source_pos[1] += self.start_socket.node.grNode.pos().y()
        self.grEdge.setSource(*source_pos)

        if self.end_socket is not None:
            end_pos = self.end_socket.getSocketPosition()
            end_pos[0] += self.end_socket.node.grNode.pos().x()
            end_pos[1] += self.end_socket.node.grNode.pos().y()
            self.grEdge.setDestination(*end_pos)
        else:
            self.grEdge.setDestination(*source_pos)

        self.grEdge.update()

    def remove_from_sockets(self):
        """Helper functions that set start and end
        :class:`~node_editor.node_socket.Socket` to None"""
        self.end_socket = None
        self.start_socket = None

    def remove(self, silent_for_socket: 'Socket' = None, silent=False):
        """Safely remove this Edge.

        Triggers Nodes':

        - :py:meth:`~node_editor.node_node.Node.onEdgeConnectionChanged`
        - :py:meth:`~node_editor.node_node.Node.onInputChanged`

        Parameters
        ----------
        silent_for_socket
        silent

        Returns
        -------

        """
        # Save sockets for triggering later events
        old_sockets = [self.start_socket, self.end_socket]

        # sometimes grEdge stay in the scene even when removed...
        self.print(" - hide grEdge")
        self.grEdge.hide()

        self.print(" - remove grEdge", self.grEdge)
        self.scene.grScene.removeItem(self.grEdge)
        self.print("   grEdge:", self.grEdge)

        self.scene.grScene.update()

        self.print("# Removing Edge", self)
        self.print(" - remove edge from all sockets")
        self.remove_from_sockets()
        self.print(" - remove edge from scene")
        self.print(old_sockets)
        try:
            self.scene.removeEdge(self)
        except ValueError:
            pass
        self.print(" - everything is done.")

        # On change, notify that the connection and eventually the inputs changed
        try:
            for socket in old_sockets:
                if socket and socket.node:
                    if silent:
                        continue
                    if silent_for_socket is not None and socket == silent_for_socket:
                        continue

                    # notify Socket's Node
                    socket.node.onEdgeConnectionChanged(self)
                    if socket.is_input:
                        socket.node.onInputChanged(self)
        except Exception as e:
            dumpException(e)

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('edge_type', self.edge_type),
            ('start', self.start_socket.id if self.start_socket is not None else None),
            ('end', self.end_socket.id if self.end_socket is not None else None)
        ])

    def deserialize(self, data: dict, hashmap=None, restore_id: bool = True):
        if hashmap is None:
            hashmap = {}
        if restore_id:
            self.id = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.edge_type = data['edge_type']

    def print(self, *args):
        if DEBUG:
            print('>Edge :', *args)
