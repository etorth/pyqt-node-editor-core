# -*- coding: utf-8 -*-
from PyQt6.QtCore import QPointF

from qdstatenodegfx import QD_StateNodeGfx
from qdsocket import *
from qdutils import *


class QD_StateNode(QD_Serializable):
    """Class representing `QD_StateNode` in the `QD_StateScene`.
    """
    StateNodeGfx_class = QD_StateNodeGfx
    Socket_class = QD_Socket

    icon = ""
    op_title = "Undefined"

    def __init__(self, scene: 'QD_StateScene', sockets: set = {SocketType.In, SocketType.Out_True, SocketType.Out_False}):
        super().__init__()
        self._title = self.__class__.op_title
        self.scene = scene

        # just to be sure, init these variables
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
        """
        Title shown in the scene

        :getter: return current QD_StateNode title
        :setter: sets QD_StateNode title and passes it to Graphics QD_StateNode class
        :type: ``str``
        """
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.gfx.title = self._title

    @property
    def pos(self):
        """
        Retrieve QD_StateNode's position in the QD_StateScene

        :return: QD_StateNode position
        :rtype: ``QPointF``
        """
        return self.gfx.pos()  # QPointF

    def setPos(self, x: float, y: float):
        """
        Sets position of the Graphics QD_StateNode

        :param x: X `QD_StateScene` position
        :param y: Y `QD_StateScene` position
        """
        self.gfx.setPos(x, y)

    def initInnerClasses(self):
        self.gfx = self.__class__.StateNodeGfx_class(self)


    def initSettings(self):
        self._max_socket_out_spacing = 30


    def initSockets(self, sockets, reset: bool = True):
        if reset:
            for sock in self.sockets:
                self.scene.gfx.removeItem(socket.gfx)
            self.sockets = []

        for type in sockets:
            self.sockets.append(self.__class__.Socket_class(node=self, socktype=type))

        self.updateSockets()


    def onEdgeConnectionChanged(self, new_edge: 'QD_Edge'):
        """
        Event handling that any connection (`QD_Edge`) has changed. Currently not used...

        :param new_edge: reference to the changed :class:`qdedge.QD_Edge`
        :type new_edge: :class:`qdedge.QD_Edge`
        """
        pass

    def onInputChanged(self, socket: 'QD_Socket'):
        """Event handling when QD_StateNode's input QD_Edge has changed. We auto-mark this `QD_StateNode` to be `Dirty` with all it's descendants

        :param socket: reference to the changed :class:`socket.QD_Socket`
        :type socket: :class:`socket.QD_Socket`
        """
        self.markDirty()
        self.markDescendantsDirty()
        self.eval()

    def onDeserialized(self, data: dict):
        """Event manually called when this node was deserialized. Currently called when node is deserialized from scene
        Passing `data` containing the data which have been deserialized """
        pass

    def onDoubleClicked(self, event):
        """Event handling double click on Graphics QD_StateNode in `QD_StateScene`"""
        pass

    def doSelect(self, new_state: bool = True):
        """Shortcut method for selecting/deselecting the `QD_StateNode`

        :param new_state: ``True`` if you want to select the `QD_StateNode`. ``False`` if you want to deselect the `QD_StateNode`
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
        if SocketType.Out_True in self.getSocketTypeSet():
            if SocketType.Out_False in self.getSocketTypeSet():
                return 2
            else:
                return 1
        else:
            return 0


    def getSocketPosition(self, type: SocketType) -> QPointF:
        assert type in SocketType
        assert type in self.getSocketTypeSet()

        if type is SocketType.In:
            return QPointF(0, self.gfx.height / 2)

        if self.getOutSocketCount() == 1:
            return QPointF(self.gfx.width, self.gfx.height / 2)

        y_spacing = min((self.gfx.height - self.gfx.title_height) / 3, self._max_socket_out_spacing)

        if type is SocketType.Out_True:
            return QPointF(self.gfx.width, self.gfx.title_height + (self.gfx.height - self.gfx.title_height - y_spacing) / 2)
        else:
            return QPointF(self.gfx.width, self.gfx.title_height + (self.gfx.height - self.gfx.title_height - y_spacing) / 2 + y_spacing)


    def getSocketScenePosition(self, socket: 'QD_Socket') -> QPointF:
        return self.gfx.pos() + self.getSocketPosition(socket.type)


    def updateConnectedEdges(self):
        for sock in self.sockets:
            for edge in sock.edges:
                edge.updatePositions()


    def updateSockets(self):
        for sock in self.sockets:
            sock.updateSocketPosition()


    def remove(self):
        """Safely remove this QD_StateNode
        """
        if confg.DEBUG:
            print("> Removing QD_StateNode", self)

        if confg.DEBUG:
            print(" - remove all edges from sockets")

        for socket in self.sockets:
            for edge in socket.edges:
                if confg.DEBUG:
                    print("    - removing from socket:", socket, "edge:", edge)
                edge.remove()

        if confg.DEBUG:
            print(" - remove gfx")

        self.scene.gfx.removeItem(self.gfx)
        self.gfx = None

        if confg.DEBUG:
            print(" - remove node from the scene")

        self.scene.removeNode(self)
        if confg.DEBUG:
            print(" - everything was done.")

    # node evaluation stuff

    def isDirty(self) -> bool:
        """Is this node marked as `Dirty`

        :return: ``True`` if `QD_StateNode` is marked as `Dirty`
        :rtype: ``bool``
        """
        return self._is_dirty

    def markDirty(self, new_value: bool = True):
        """Mark this `QD_StateNode` as `Dirty`. See :ref:`evaluation` for more

        :param new_value: ``True`` if this `QD_StateNode` should be `Dirty`. ``False`` if you want to un-dirty this `QD_StateNode`
        :type new_value: ``bool``
        """
        self._is_dirty = new_value
        if self._is_dirty:
            self.onMarkedDirty()

    def onMarkedDirty(self):
        """Called when this `QD_StateNode` has been marked as `Dirty`. This method is supposed to be overriden"""
        pass

    def markChildrenDirty(self, new_value: bool = True):
        """Mark all first level children of this `QD_StateNode` to be `Dirty`. Not this `QD_StateNode` it self. Not other descendants

        :param new_value: ``True`` if children should be `Dirty`. ``False`` if you want to un-dirty children
        :type new_value: ``bool``
        """
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)

    def markDescendantsDirty(self, new_value: bool = True):
        """Mark all children and descendants of this `QD_StateNode` to be `Dirty`. Not this `QD_StateNode` it self

        :param new_value: ``True`` if children and descendants should be `Dirty`. ``False`` if you want to un-dirty children and descendants
        :type new_value: ``bool``
        """
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)
            other_node.markChildrenDirty(new_value)

    def isInvalid(self) -> bool:
        """Is this node marked as `Invalid`?

        :return: ``True`` if `QD_StateNode` is marked as `Invalid`
        :rtype: ``bool``
        """
        return self._is_invalid

    def markInvalid(self, new_value: bool = True):
        """Mark this `QD_StateNode` as `Invalid`. See :ref:`evaluation` for more

        :param new_value: ``True`` if this `QD_StateNode` should be `Invalid`. ``False`` if you want to make this `QD_StateNode` valid
        :type new_value: ``bool``
        """
        self._is_invalid = new_value
        if self._is_invalid: self.onMarkedInvalid()

    def onMarkedInvalid(self):
        """Called when this `QD_StateNode` has been marked as `Invalid`. This method is supposed to be overriden"""
        pass

    def markChildrenInvalid(self, new_value: bool = True):
        """Mark all first level children of this `QD_StateNode` to be `Invalid`. Not this `QD_StateNode` it self. Not other descendants

        :param new_value: ``True`` if children should be `Invalid`. ``False`` if you want to make children valid
        :type new_value: ``bool``
        """
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)

    def markDescendantsInvalid(self, new_value: bool = True):
        """Mark all children and descendants of this `QD_StateNode` to be `Invalid`. Not this `QD_StateNode` it self

        :param new_value: ``True`` if children and descendants should be `Invalid`. ``False`` if you want to make children and descendants valid
        :type new_value: ``bool``
        """
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)
            other_node.markChildrenInvalid(new_value)


    def evalOperation(self, input1, input2):
        return 123


    def evalImplementation(self):
        inputs = self.getInputs()
        if not inputs:
            self.markInvalid()
            self.markDescendantsDirty()
            self.gfx.setToolTip('Node has no input connected')
            return None

        i1 = inputs[0]
        i2 = inputs[0]

        val = self.evalOperation(i1.eval(), i2.eval())
        self.value = val
        self.markDirty(False)
        self.markInvalid(False)
        self.gfx.setToolTip("")

        self.markDescendantsDirty()
        self.evalChildren()

        return val

    def eval(self):
        if not self.isDirty() and not self.isInvalid():
            print(" _> returning cached %s value:" % self.__class__.__name__, self.value)
            return self.value

        try:

            val = self.evalImplementation()
            return val
        except ValueError as e:
            self.markInvalid()
            self.gfx.setToolTip(str(e))
            self.markDescendantsDirty()
        except Exception as e:
            self.markInvalid()
            self.gfx.setToolTip(str(e))
            utils.dumpExcept(e)

    def evalChildren(self):
        """Evaluate all children of this `QD_StateNode`"""
        for node in self.getChildrenNodes():
            node.eval()

    def getChildrenNodes(self) -> 'List[QD_StateNode]':
        """Retreive all first-level children connected to this QD_StateNode output
        """
        other_nodes = []
        for sock in self.sockets:
            if sock.is_output:
                for edge in sock.edges:
                    other_nodes.append(edge.getOtherSocket(sock).node)
        return other_nodes

    def getInputs(self):
        sockin = self.getSocket(SocketType.In)
        if sockin is None:
            return None
        return [edge.getOtherSocket(sockin).node for edge in sockin.edges]

    def getOutput(self, socktype: SocketType):
        sockout = self.getSocket(socktype)
        if sockout is None:
            return None

        if sockout.edges:
            return sockout.edges[0].getOtherSocket(sockout).node
        return None

    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('position', (self.gfx.scenePos().x(), self.gfx.scenePos().y())),
            ('sockets', [sock.serialize() for sock in self.sockets]),
            ('op_code', self.__class__.op_code), # added by @register_opnode
        ])

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

        except Exception as e:
            utils.dumpExcept(e)

        return True
