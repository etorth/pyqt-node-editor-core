# -*- coding: utf-8 -*-
from PyQt6.QtCore import QPointF

from qdopnodegfx import QD_OpNodeGfx
from qdopnodecontent import *
from qdsocket import *
from qdutils import *
from qdnode import QD_Node


class QD_OpNode(QD_Node):
    NodeGfx_class = QD_OpNodeGfx
    NodeContent_class = QD_OpNodeContent

    icon = ""
    op_title = "Undefined"

    def __init__(self, scene: 'QD_StateScene', sockets: set = {SocketType.In, SocketType.Out_True, SocketType.Out_False}):
        super().__init__(scene)
        self._title = self.__class__.op_title

        outtypes = set([sock.cast_type() for sock in sockets if sock is not SocketType.In])
        if len(outtypes) > 1:
            raise ValueError(sockets)


        # just to be sure, init these variables
        self.content = None
        self.gfx = None

        self.sockets = []

        self.initInnerClasses()
        self.initSettings()

        self.title = self.__class__.op_title

        self.scene.addNode(self)
        self.scene.gfx.addItem(self.gfx)

        self.initSockets(sockets)

        # dirty and evaluation
        self._is_dirty = False
        self._is_invalid = False

        self.value = None
        self.markDirty()

    def __str__(self):
        return "<%s:%s %s..%s>" % (self.title, self.__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.gfx.title = self._title

    @property
    def pos(self):
        return self.gfx.pos()  # QPointF


    @property
    def output_type(self):
        for socktype in self.getSocketTypeSet():
            if socktype is not SocketType.In:
                return socktype.cast_type()
        return None


    def setPos(self, x: float, y: float):
        """
        Sets position of the Graphics QD_OpNode

        :param x: X `QD_StateScene` position
        :param y: Y `QD_StateScene` position
        """
        self.gfx.setPos(x, y)

    def initInnerClasses(self):
        node_content_class = self.getNodeContentClass()
        graphics_node_class = self.getGraphicsNodeClass()

        if node_content_class is not None:
            self.content = node_content_class(self)

        if graphics_node_class is not None:
            self.gfx = graphics_node_class(self)

    def getNodeContentClass(self):
        return self.__class__.NodeContent_class

    def getGraphicsNodeClass(self):
        return self.__class__.NodeGfx_class

    def initSettings(self):
        self._max_socket_out_spacing = 30


    def initSockets(self, sockets, reset: bool = True):
        if reset:
            for sock in self.sockets:
                self.scene.gfx.removeItem(sock.gfx)
            self.sockets = []

        for type in sockets:
            self.sockets.append(self.__class__.Socket_class(node=self, socktype=type))

        self.updateSockets()


    def onDeserialized(self, data: dict):
        """Event manually called when this node was deserialized. Currently called when node is deserialized from scene
        Passing `data` containing the data which have been deserialized """
        pass

    def onDoubleClicked(self, event):
        """Event handling double click on Graphics QD_OpNode in `QD_StateScene`"""
        self.content.gfx.mouseDoubleClickEvent(event)

    def doSelect(self, new_state: bool = True):
        """Shortcut method for selecting/deselecting the `QD_OpNode`

        :param new_state: ``True`` if you want to select the `QD_OpNode`. ``False`` if you want to deselect the `QD_OpNode`
        :type new_state: ``bool``
        """
        self.gfx.doSelect(new_state)

    def isSelected(self):
        return self.gfx.isSelected()

    def getSocket(self, socktype: SocketType) -> [QD_Socket, None]:
        for sock in self.sockets:
            if sock.type is socktype:
                return sock
        return None

    def getSocketTypeSet(self):
        return set([sock.type for sock in self.sockets])


    def getOutSocketCount(self):
        sockset = self.getSocketTypeSet()
        if SocketType.In in sockset:
            return len(sockset) - 1
        else:
            return len(sockset)


    def getSocketPosition(self, socktype: SocketType) -> QPointF:
        assert socktype in SocketType
        assert socktype in self.getSocketTypeSet()

        if socktype is SocketType.In:
            return QPointF(0, self.gfx.height / 2)

        if self.getOutSocketCount() == 1:
            return QPointF(self.gfx.width, self.gfx.height / 2)

        if self.output_type is bool or self.getOutSocketCount() == 2:
            y_spacing = min((self.gfx.height - self.gfx.title_height) / 3, self._max_socket_out_spacing)

            if socktype is SocketType.Out_True or socktype is SocketType.IndexOut_0:
                return QPointF(self.gfx.width, self.gfx.title_height + (self.gfx.height - self.gfx.title_height - y_spacing) / 2)
            else:
                return QPointF(self.gfx.width, self.gfx.title_height + (self.gfx.height - self.gfx.title_height - y_spacing) / 2 + y_spacing)

        else:
            return QPointF(self.gfx.width, self.gfx.height / 4 + (self.gfx.height / 2 / (self.getOutSocketCount() - 1)) * socktype.as_index)


    def getSocketScenePosition(self, socket: 'QD_Socket') -> QPointF:
        return self.gfx.pos() + self.getSocketPosition(socket.type)


    def isDirty(self) -> bool:
        return self._is_dirty

    def markDirty(self, new_value: bool = True):
        self._is_dirty = new_value
        if self._is_dirty:
            self.onMarkedDirty()


    def getOutput(self, socktype: SocketType):
        sockout = self.getSocket(socktype)
        if sockout is None:
            return None

        if sockout.edges:
            return sockout.edges[0].getOtherSocket(sockout).node
        return None

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'position': (self.gfx.scenePos().x(), self.gfx.scenePos().y()),
            'sockets': [sock.serialize() for sock in self.sockets],
            'content': self.content.serialize(),
            'op_code': self.__class__.op_code, # added by @opNodeRegister
        }

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        try:
            if restore_id:
                self.id = data['id']

            hashmap[data['id']] = self

            self.setPos(*data['position'])
            self.title = data['title']

            for sockdata in data['sockets']:
                found = None
                for sock in self.sockets:
                    if sock.type == sockdata['type']:
                        found = sock
                        break

                if found is None:
                    found = self.__class__.Socket_class(node=self, socktype=SocketType(sockdata['type']))
                    self.sockets.append(found)

                found.deserialize(sockdata, hashmap, restore_id)

            self.content.deserialize(data['content'], hashmap)
        except Exception as e:
            utils.dumpExcept(e)

        return True
