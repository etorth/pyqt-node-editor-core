# -*- coding: utf-8 -*-
"""A module containing NodeEditor's class for representing QD_Socket and QD_Socket Position Constants.
"""
from collections import OrderedDict
from qdserializable import QD_Serializable
from qdsocketgfx import QD_SocketGfx
from qdutils import *

LEFT_TOP = 1  #:
LEFT_CENTER = 2  #:
LEFT_BOTTOM = 3  #:
RIGHT_TOP = 4  #:
RIGHT_CENTER = 5  #:
RIGHT_BOTTOM = 6  #:

DEBUG = True
DEBUG_REMOVE_WARNINGS = False


class QD_Socket(QD_Serializable):
    SocketGfx_class = QD_SocketGfx

    """Class representing QD_Socket."""

    def __init__(self, node: 'QD_Node', index: int = 0, position: int = LEFT_TOP, socket_type: int = 1, multi_edges: bool = True, count_on_this_node_side: int = 1, is_input: bool = False):
        """
        :param node: reference to the :class:`node.QD_Node` containing this `QD_Socket`
        :type node: :class:`node.QD_Node`
        :param index: Current index of this socket in the position
        :type index: ``int``
        :param position: QD_Socket position. See :ref:`socket-position-constants`
        :param socket_type: Constant defining type(color) of this socket
        :param multi_edges: Can this socket have multiple `Edges` connected?
        :type multi_edges: ``bool``
        :param count_on_this_node_side: number of total sockets on this position
        :type count_on_this_node_side: ``int``
        :param is_input: Is this an input `QD_Socket`?
        :type is_input: ``bool``

        :Instance Attributes:

            - **node** - reference to the :class:`node.QD_Node` containing this `QD_Socket`
            - **edges** - list of `Edges` connected to this `QD_Socket`
            - **gfx** - reference to the :class:`qdsocketgfx.QD_SocketGfx`
            - **position** - QD_Socket position. See :ref:`socket-position-constants`
            - **index** - Current index of this socket in the position
            - **socket_type** - Constant defining type(color) of this socket
            - **count_on_this_node_side** - number of sockets on this position
            - **is_multi_edges** - ``True`` if `QD_Socket` can contain multiple `Edges`
            - **is_input** - ``True`` if this socket serves for Input
            - **is_output** - ``True`` if this socket serves for Output
        """
        super().__init__()

        self.node = node
        self.position = position
        self.index = index
        self.socket_type = socket_type
        self.count_on_this_node_side = count_on_this_node_side
        self.is_multi_edges = multi_edges
        self.is_input = is_input
        self.is_output = not self.is_input

        if confg.DEBUG:
            print("QD_Socket -- creating with", self.index, self.position, "for nodeeditor", self.node)

        self.gfx = self.__class__.SocketGfx_class(self)
        self.setSocketPosition()
        self.edges = []

    def __str__(self):
        return "<QD_Socket #%d %s %s..%s>" % (
            self.index, "ME" if self.is_multi_edges else "SE", hex(id(self))[2:5], hex(id(self))[-3:]
        )

    def delete(self):
        """Delete this `QD_Socket` from graphics scene for sure
        """
        self.gfx.setParentItem(None)
        self.node.scene.gfx.removeItem(self.gfx)
        del self.gfx

    def changeSocketType(self, new_socket_type: int) -> bool:
        """Change the QD_Socket Type

        :param new_socket_type: new socket type
        :type new_socket_type: ``int``
        :return: Returns ``True`` if the socket type was actually changed
        :rtype: ``bool``
        """
        if self.socket_type != new_socket_type:
            self.socket_type = new_socket_type
            self.gfx.changeSocketType()
            return True
        return False

    def setSocketPosition(self):
        """Helper function to set `Graphics QD_Socket` position. Exact socket position is calculated
        inside :class:`node.QD_Node`."""
        self.gfx.setPos(*self.node.getSocketPosition(self.index, self.position, self.count_on_this_node_side))

    def getSocketPosition(self):
        """
        :return: Returns this `QD_Socket` position according the implementation stored in
            :class:`node.QD_Node`
        :rtype: ``x, y`` position
        """
        if confg.DEBUG:
            print("  GSP: ", self.index, self.position, "nodeeditor:", self.node)

        res = self.node.getSocketPosition(self.index, self.position, self.count_on_this_node_side)

        if confg.DEBUG:
            print("  res", res)

        return res

    def hasAnyEdge(self) -> bool:
        """
        Returns ``True`` if any :class:`qdedge.QD_Edge` is connectected to this socket

        :return: ``True`` if any :class:`qdedge.QD_Edge` is connected to this socket
        :rtype: ``bool``
        """
        return len(self.edges) > 0

    def isConnected(self, edge: 'QD_Edge') -> bool:
        """Returns ``True`` if :class:`qdedge.QD_Edge` is connected to this `QD_Socket`

        :param edge: :class:`qdedge.QD_Edge` to check if it is connected to this `QD_Socket`
        :type edge: :class:`qdedge.QD_Edge`
        :return: ``True`` if `QD_Edge` is connected to this socket
        :rtype: ``bool``
        """
        return edge in self.edges

    def addEdge(self, edge: 'QD_Edge'):
        """
        Append an QD_Edge to the list of connected Edges

        :param edge: :class:`qdedge.QD_Edge` to connect to this `QD_Socket`
        :type edge: :class:`qdedge.QD_Edge`
        """
        self.edges.append(edge)

    def removeEdge(self, edge: 'QD_Edge'):
        """
        Disconnect passed :class:`qdedge.QD_Edge` from this `QD_Socket`
        :param edge: :class:`qdedge.QD_Edge` to disconnect
        :type edge: :class:`qdedge.QD_Edge`
        """
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            if DEBUG_REMOVE_WARNINGS:
                print("!W:", "QD_Socket::removeEdge", "wanna remove edge", edge,
                      "from self.edges but it's not in the list!")

    def removeAllEdges(self, silent=False):
        """Disconnect all `Edges` from this `QD_Socket`"""
        while self.edges:
            edge = self.edges.pop(0)
            if silent:
                edge.remove(silent_for_socket=self)
            else:
                edge.remove()  # just remove all with notifications

    def determineMultiEdges(self, data: dict) -> bool:
        """
        Deserialization helper function. In our tutorials we create new version of graph data format.
        This function is here to help solve the issue of opening older files in the newer format.
        If the 'multi_edges' param is missing in the dictionary, we determine if this `QD_Socket`
        should support multiple `Edges`.

        :param data: `QD_Socket` data in ``dict`` format for deserialization
        :type data: ``dict``
        :return: ``True`` if this `QD_Socket` should support multi_edges
        """
        if 'multi_edges' in data:
            return data['multi_edges']
        else:
            # probably older version of file, make RIGHT socket multiedged by default
            return data['position'] in (RIGHT_BOTTOM, RIGHT_TOP)

    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('multi_edges', self.is_multi_edges),
            ('position', self.position),
            ('socket_type', self.socket_type),
        ])

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        if restore_id: self.id = data['id']
        self.is_multi_edges = self.determineMultiEdges(data)
        self.changeSocketType(data['socket_type'])
        hashmap[data['id']] = self
        return True
