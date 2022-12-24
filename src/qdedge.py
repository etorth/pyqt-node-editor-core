# -*- coding: utf-8 -*-
from enum import Enum, unique
from qdserializable import QD_Serializable
from qdutils import *
from qdedgegfx import *

@unique
class EdgeType(int, Enum):
    Direct = 0
    Bezier = 1

class QD_Edge(QD_Serializable):
    """Class for representing QD_Edge in NodeEditor.
    """

    def __init__(self, scene: 'QD_StateScene', start_socket: 'QD_Socket' = None, end_socket: 'QD_Socket' = None, edge_type=EdgeType.Direct):
        """

        :param scene: Reference to the :py:class:`scene.QD_StateScene`
        :type scene: :py:class:`scene.QD_StateScene`
        :param start_socket: Reference to the starting socket
        :type start_socket: :py:class:`socket.QD_Socket`
        :param end_socket: Reference to the End socket or ``None``
        :type end_socket: :py:class:`socket.QD_Socket` or ``None``
        :param edge_type: Constant determining type of edge. See :ref:`edge-type-constants`

        :Instance Attributes:

            - **scene** - reference to the :class:`scene.QD_StateScene`
            - **gfx** - Instance of :class:`qdedgegfx.QD_EdgeGfx` subclass handling graphical representation in the ``QGraphicsScene``.
        """
        super().__init__()
        self.scene = scene

        # default init
        self._start_socket = None
        self._end_socket = None

        self.start_socket = start_socket
        self.end_socket = end_socket
        self.edge_type = edge_type

        self.scene.addEdge(self)

    def __str__(self):
        return "<QD_Edge %s..%s -- S:%s E:%s>" % (hex(id(self))[2:5], hex(id(self))[-3:], self.start_socket, self.end_socket)

    @property
    def start_socket(self):
        """
        Start socket

        :getter: Returns start :class:`socket.QD_Socket`
        :setter: Sets start :class:`socket.QD_Socket` safely
        :type: :class:`socket.QD_Socket`
        """
        return self._start_socket

    @start_socket.setter
    def start_socket(self, value):
        # if we were assigned to some socket before, delete us from the socket
        if self._start_socket is not None:
            self._start_socket.removeEdge(self)

        # assign new start socket
        self._start_socket = value
        # addEdge to the QD_Socket class
        if self.start_socket is not None:
            self.start_socket.addEdge(self)

    @property
    def end_socket(self):
        """
        End socket

        :getter: Returns end :class:`socket.QD_Socket` or ``None`` if not set
        :setter: Sets end :class:`socket.QD_Socket` safely
        :type: :class:`socket.QD_Socket` or ``None``
        """
        return self._end_socket

    @end_socket.setter
    def end_socket(self, value):
        # if we were assigned to some socket before, delete us from the socket
        if self._end_socket is not None:
            self._end_socket.removeEdge(self)

        # assign new end socket
        self._end_socket = value
        # addEdge to the QD_Socket class
        if self.end_socket is not None:
            self.end_socket.addEdge(self)

    @property
    def edge_type(self):
        """QD_Edge type

        :getter: get edge type constant for current ``QD_Edge``. See :ref:`edge-type-constants`
        :setter: sets new edge type. On background, creates new :class:`qdedgegfx.QD_EdgeGfx`
            child class if necessary, adds this ``QGraphicsPathItem`` to the ``QGraphicsScene`` and updates edge sockets
            positions.
        """
        return self._edge_type

    @edge_type.setter
    def edge_type(self, value):
        if hasattr(self, 'gfx') and self.gfx is not None:
            self.scene.gfx.removeItem(self.gfx)

        self._edge_type = value
        edgeClass = self.determineEdgeClass(self.edge_type)
        self.gfx = edgeClass(self)

        self.scene.gfx.addItem(self.gfx)

        if self.start_socket is not None:
            self.updatePositions()

    def determineEdgeClass(self, edge_type: int):
        """
        Determine Graphics QD_Edge Class from provided `edge_type`
        :param edge_type: ``int`` type of edge
        :return: gfx class
        :rtype: class of `gfx`
        """
        edge_class = GfxEdgeBezier
        if edge_type == EdgeType.Direct:
            edge_class = GfxEdgeDirect
        return edge_class

    def getOtherSocket(self, known_socket: 'QD_Socket'):
        """
        Returns the oposite socket on this ``QD_Edge``

        :param known_socket: Provide known :class:`socket.QD_Socket` to be able to determine the oposite one.
        :type known_socket: :class:`socket.QD_Socket`
        :return: The oposite socket on this ``QD_Edge`` or ``None``
        :rtype: :class:`socket.QD_Socket` or ``None``
        """
        return self.start_socket if known_socket == self.end_socket else self.end_socket

    def doSelect(self, new_state: bool = True):
        """
        Provide the safe selecting/deselecting operation. In the background it takes care about the flags, norifications
        and storing history for undo/redo.

        :param new_state: ``True`` if you want to select the ``QD_Edge``, ``False`` if you want to deselect the ``QD_Edge``
        :type new_state: ``bool``
        """
        self.gfx.doSelect(new_state)

    def updatePositions(self):
        """
        Updates the internal `Graphics QD_Edge` positions according to the start and end :class:`socket.QD_Socket`.
        This should be called if you update ``QD_Edge`` positions.
        """
        source_pos = self.start_socket.getSocketPosition() + self.start_socket.node.gfx.pos()
        self.gfx.setSource(source_pos.x(), source_pos.y())

        if self.end_socket is not None:
            end_pos = self.end_socket.getSocketPosition() + self.end_socket.node.gfx.pos()
            self.gfx.setDestination(end_pos.x(), end_pos.y())
        else:
            self.gfx.setDestination(source_pos.x(), source_pos.y())

        self.gfx.update()

    def remove_from_sockets(self):
        """
        Helper function which sets start and end :class:`socket.QD_Socket` to ``None``
        """
        self.end_socket = None
        self.start_socket = None

    def remove(self, silent_for_socket: 'QD_Socket' = None, silent=False):
        """Safely remove this QD_Edge.

        Removes `Graphics QD_Edge` from the ``QGraphicsScene`` and it's reference to all GC to clean it up.
        Notifies nodes previously connected :class:`node.QD_Node` (s) about this event.

        Triggers Nodes':

        - :py:meth:`node.QD_Node.onEdgeConnectionChanged`
        - :py:meth:`node.QD_Node.onInputChanged`

        :param silent_for_socket: :class:`socket.QD_Socket` of a :class:`node.QD_Node` which
            won't be notified, when this ``QD_Edge`` is going to be removed
        :type silent_for_socket: :class:`socket.QD_Socket`
        :param silent: ``True`` if no events should be triggered during removing
        :type silent: ``bool``
        """
        old_sockets = [self.start_socket, self.end_socket]

        # ugly hack, since I noticed that even when you remove gfx from scene,
        # sometimes it stays there! How dare you Qt!
        if confg.DEBUG:
            print(" - hide gfx")
        self.gfx.hide()

        if confg.DEBUG:
            print(" - remove gfx", self.gfx)

        self.scene.gfx.removeItem(self.gfx)
        if confg.DEBUG:
            print("   gfx:", self.gfx)

        self.scene.gfx.update()

        if confg.DEBUG:
            print("# Removing QD_Edge", self)

        if confg.DEBUG:
            print(" - remove edge from all sockets")

        self.remove_from_sockets()
        if confg.DEBUG:
            print(" - remove edge from scene")

        try:
            self.scene.removeEdge(self)
        except ValueError:
            pass

        if confg.DEBUG:
            print(" - everything is done.")

        try:
            # notify nodes from old sockets
            for socket in old_sockets:
                if socket and socket.node:
                    if silent:
                        continue
                    if silent_for_socket is not None and socket == silent_for_socket:
                        # if we requested silence for QD_Socket and it's this one, skip notifications
                        continue

                    # notify QD_Socket's QD_Node
                    socket.node.onEdgeConnectionChanged(self)
                    if socket.is_input: socket.node.onInputChanged(socket)

        except Exception as e:
            utils.dumpExcept(e)

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'edge_type': self.edge_type,
            'start': self.start_socket.id if self.start_socket is not None else None,
            'end': self.end_socket.id if self.end_socket is not None else None,
        }

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        if restore_id: self.id = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.edge_type = data['edge_type']
