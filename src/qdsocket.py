# -*- coding: utf-8 -*-
from qdutils import *
from qdsocketgfx import *
from qdserializable import QD_Serializable

class QD_Socket(QD_Serializable):
    SocketGfx_class = QD_SocketGfx

    def __init__(self, node: 'QD_Node', socktype: SocketType):
        super().__init__()

        self.node = node
        self.type = socktype

        self.edges = []
        self.gfx = self.__class__.SocketGfx_class(self)

    def __str__(self):
        return "<QD_Socket %s %s>" % (id(self), self.type)

    @property
    def is_multi_edges(self) -> bool:
        return self.type in [SocketType.In, SocketType.PulseOut]

    @property
    def is_input(self) -> bool:
        return self.type.is_in

    @property
    def is_output(self) -> bool:
        return self.type.is_out

    def delete(self):
        """Delete this QD_Socket from graphics scene for sure
        """
        self.gfx.setParentItem(None)
        self.node.scene.gfx.removeItem(self.gfx)
        del self.gfx

    def changeSocketType(self, socktype: SocketType):
        if self.type is not socktype:
            self.type = socktype
            self.gfx.changeSocketType()

    def updateSocketPosition(self):
        self.gfx.setPos(self.getSocketPosition())

    def getSocketPosition(self):
        """Position of socket it should be, not it actually be, which is self.gfx.pos()
        """
        return self.node.getSocketPosition(self.type)

    def hasEdge(self) -> bool:
        return len(self.edges) > 0

    def isConnected(self, edge: 'QD_Edge') -> bool:
        return edge in self.edges

    def addEdge(self, edge: 'QD_Edge'):
        self.edges.append(edge)

    def removeEdge(self, edge: 'QD_Edge'):
        if edge in self.edges:
            self.edges.remove(edge)

    def removeAllEdges(self, silent=False):
        while self.edges:
            edge = self.edges.pop(0)
            edge.remove(silent_for_socket=(self if silent else None))

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'type': self.type,
        }

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True):
        if restore_id:
            self.id = data['id']

        self.changeSocketType(SocketType(data['type']))
        hashmap[data['id']] = self
