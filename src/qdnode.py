# -*- coding: utf-8 -*-
from PyQt6.QtCore import QPointF

from qdsocket import QD_Socket
from qdsocketgfx import QD_SocketGfx, SocketType
from qdserializable import QD_Serializable

class QD_Node(QD_Serializable):
    Socket_class = QD_Socket


    def __init__(self, scene: 'QD_Scene'):
        super().__init__()
        self.scene = scene
        self._status = 0

    def isDirty(self) -> bool:
        return self._status == 1


    def isInvalid(self) -> bool:
        return self._status == 2


    def markDirty(self, val: bool):
        pass

    def getSocket(self, socktype: SocketType) -> [QD_Socket, None]:
        for sock in self.sockets:
            if sock.type is socktype:
                return sock
        return None

    def getSocketTypeSet(self):
        return set([sock.type for sock in self.sockets])


    def getOutSocketCount(self):
        count = 0
        for socktype in self.getSocketTypeSet():
            if socktype.is_out:
                count += 1
        return count


    def getInSocketCount(self):
        count = 0
        for socktype in self.getSocketTypeSet():
            if socktype.is_in:
                count += 1
        return count


    def getSocketPosition(self, socktype: SocketType) -> QPointF:
        assert socktype in SocketType
        assert socktype in self.getSocketTypeSet()

        if socktype.is_in:
            if self.getInSocketCount() == 1:
                return QPointF(0, self.gfx.height / 2)
            else:
                y_in_spacing = min((self.gfx.height - self.gfx.title_height) / 3, self._max_socket_in_spacing)
                if (socktype is SocketType.In) == self.pulse_on_bottom:
                    return QPointF(0, self.gfx.title_height + (self.gfx.height - self.gfx.title_height - y_in_spacing) / 2)
                else:
                    return QPointF(0, self.gfx.title_height + (self.gfx.height - self.gfx.title_height - y_in_spacing) / 2 + y_in_spacing)

        if self.getOutSocketCount() == 1:
            return QPointF(self.gfx.width, self.gfx.height / 2)

        y_out_spacing = min((self.gfx.height - self.gfx.title_height) / 3, self._max_socket_out_spacing)

        if socktype is SocketType.Out_True:
            return QPointF(self.gfx.width, self.gfx.title_height + (self.gfx.height - self.gfx.title_height - y_out_spacing) / 2)
        else:
            return QPointF(self.gfx.width, self.gfx.title_height + (self.gfx.height - self.gfx.title_height - y_out_spacing) / 2 + y_out_spacing)


    def getInputs(self):
        sockin = self.getSocket(SocketType.In)
        if sockin is None:
            return None
        return [edge.getOtherSocket(sockin).node for edge in sockin.edges if hasattr(edge.getOtherSocket(sockin), 'node')]


    def getOutput(self, socktype: SocketType):
        sockout = self.getSocket(socktype)
        if sockout is None:
            return None

        if sockout.edges:
            return sockout.edges[0].getOtherSocket(sockout).node
        return None


    def getRoots(self):
        """can be more than one root node

           +---+        +---+       +---+
           | 1 +--------+ 2 +-------+ 4 |
           |   |.....   +---+    +--+   |
           +---+    .            |  +---+
                    .            |
                    .   +---+    |
                    ....| 3 +----+
                        +---+

           the dash line has not been conencted yet
           so for node-4, it has two roots now: node-1 and node-3
        """
        result = []
        nextnodes = [self]

        while nextnodes:
            currnode = nextnodes.pop(0)
            inputs = currnode.getInputs()

            if inputs:
                nextnodes += inputs
            else:
                result.append(currnode)
        return result


    def updateConnectedEdges(self):
        for sock in self.sockets:
            for edge in sock.edges:
                edge.updatePositions()


    def onEdgeConnectionChanged(self, new_edge: 'QD_Edge'):
        pass
