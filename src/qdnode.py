# -*- coding: utf-8 -*-
"""
A module containing NodeEditor's class for representing `QD_Node`.
"""
from nodegfx import NodeGfx
from qdnodecontent import QD_NodeContent
from qsocket import *
from qdutils import *


class QD_Node(QD_Serializable):
    """Class representing `QD_Node` in the `QD_Scene`.
    """
    NodeGfx_class = NodeGfx
    NodeContent_class = QD_NodeContent
    Socket_class = Socket

    icon = ""
    op_title = "Undefined"

    def __init__(self, scene: 'QD_Scene', inputs: list = [2, 2], outputs: list = [1]):
        """
        :param scene: reference to the :class:`~nodeeditor.scene.QD_Scene`
        :type scene: :class:`~nodeeditor.scene.QD_Scene`
        :param inputs: list of :class:`~nodeeditor.socket.Socket` types from which the `Sockets` will be auto created
        :param outputs: list of :class:`~nodeeditor.socket.Socket` types from which the `Sockets` will be auto created

        :Instance Attributes:

            - **scene** - reference to the :class:`~nodeeditor.scene.QD_Scene`
            - **gfx** - Instance of :class:`~nodeeditor.nodegfx.NodeGfx` handling graphical representation in the ``QGraphicsScene``. Automatically created in constructor
            - **content** - Instance of :class:`~nodeeditor.node_graphics_content.GfxContent` which is child of ``QWidget`` representing container for all inner widgets inside of the QD_Node. Automatically created in constructor
            - **inputs** - list containin Input :class:`~nodeeditor.socket.Socket` instances
            - **outputs** - list containin Output :class:`~nodeeditor.socket.Socket` instances

        """
        super().__init__()
        self._title = self.__class__.op_title
        self.scene = scene

        # just to be sure, init these variables
        self.content = None
        self.gfx = None

        self.initInnerClasses()
        self.initSettings()

        self.title = self.__class__.op_title

        self.scene.addNode(self)
        self.scene.gfx.addItem(self.gfx)

        # create socket for inputs and outputs
        self.inputs = []
        self.outputs = []
        self.initSockets(inputs, outputs)

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

        :getter: return current QD_Node title
        :setter: sets QD_Node title and passes it to Graphics QD_Node class
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
        Retrieve QD_Node's position in the QD_Scene

        :return: QD_Node position
        :rtype: ``QPointF``
        """
        return self.gfx.pos()  # QPointF

    def setPos(self, x: float, y: float):
        """
        Sets position of the Graphics QD_Node

        :param x: X `QD_Scene` position
        :param y: Y `QD_Scene` position
        """
        self.gfx.setPos(x, y)

    def initInnerClasses(self):
        """Sets up graphics QD_Node (PyQt) and Content Widget"""
        node_content_class = self.getNodeContentClass()
        graphics_node_class = self.getGraphicsNodeClass()

        if node_content_class is not None:
            self.content = node_content_class(self)

        if graphics_node_class is not None:
            self.gfx = graphics_node_class(self)

    def getNodeContentClass(self):
        """Returns class representing nodeeditor content"""
        return self.__class__.NodeContent_class

    def getGraphicsNodeClass(self):
        return self.__class__.NodeGfx_class

    def initSettings(self):
        """Initialize properties and socket information"""
        self.socket_spacing = 22

        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER
        self.input_multi_edged = False
        self.output_multi_edged = True
        self.socket_offsets = {
            LEFT_BOTTOM: -1,
            LEFT_CENTER: -1,
            LEFT_TOP: -1,
            RIGHT_BOTTOM: 1,
            RIGHT_CENTER: 1,
            RIGHT_TOP: 1,
        }

    def initSockets(self, inputs: list, outputs: list, reset: bool = True):
        """Create sockets for inputs and outputs

        :param inputs: list of Socket Types (int)
        :type inputs: ``list``
        :param outputs: list of Socket Types (int)
        :type outputs: ``list``
        :param reset: if ``True`` destroys and removes old `Sockets`
        :type reset: ``bool``
        """

        if reset:
            # clear old sockets
            if hasattr(self, 'inputs') and hasattr(self, 'outputs'):
                # remove gfxSockets from scene
                for socket in (self.inputs + self.outputs):
                    self.scene.gfx.removeItem(socket.gfx)
                self.inputs = []
                self.outputs = []

        # create new sockets
        counter = 0
        for item in inputs:
            socket = self.__class__.Socket_class(
                node=self, index=counter, position=self.input_socket_position,
                socket_type=item, multi_edges=self.input_multi_edged,
                count_on_this_node_side=len(inputs), is_input=True
            )
            counter += 1
            self.inputs.append(socket)

        counter = 0
        for item in outputs:
            socket = self.__class__.Socket_class(
                node=self, index=counter, position=self.output_socket_position,
                socket_type=item, multi_edges=self.output_multi_edged,
                count_on_this_node_side=len(outputs), is_input=False
            )
            counter += 1
            self.outputs.append(socket)

    def onEdgeConnectionChanged(self, new_edge: 'QD_Edge'):
        """
        Event handling that any connection (`QD_Edge`) has changed. Currently not used...

        :param new_edge: reference to the changed :class:`~nodeeditor.qdedge.QD_Edge`
        :type new_edge: :class:`~nodeeditor.qdedge.QD_Edge`
        """
        pass

    def onInputChanged(self, socket: 'Socket'):
        """Event handling when QD_Node's input QD_Edge has changed. We auto-mark this `QD_Node` to be `Dirty` with all it's
        descendants

        :param socket: reference to the changed :class:`~nodeeditor.socket.Socket`
        :type socket: :class:`~nodeeditor.socket.Socket`
        """
        self.markDirty()
        self.markDescendantsDirty()
        self.eval()

    def onDeserialized(self, data: dict):
        """Event manually called when this node was deserialized. Currently called when node is deserialized from scene
        Passing `data` containing the data which have been deserialized """
        pass

    def onDoubleClicked(self, event):
        """Event handling double click on Graphics QD_Node in `QD_Scene`"""
        pass

    def doSelect(self, new_state: bool = True):
        """Shortcut method for selecting/deselecting the `QD_Node`

        :param new_state: ``True`` if you want to select the `QD_Node`. ``False`` if you want to deselect the `QD_Node`
        :type new_state: ``bool``
        """
        self.gfx.doSelect(new_state)

    def isSelected(self):
        """Returns ``True`` if current `QD_Node` is selected"""
        return self.gfx.isSelected()

    def getSocketPosition(self, index: int, position: int, num_out_of: int = 1) -> '(x, y)':
        """
        Get the relative `x, y` position of a :class:`~nodeeditor.socket.Socket`. This is used for placing
        the `Graphics Sockets` on `Graphics QD_Node`.

        :param index: Order number of the Socket. (0, 1, 2, ...)
        :type index: ``int``
        :param position: `Socket Position Constant` describing where the Socket is located. See :ref:`socket-position-constants`
        :type position: ``int``
        :param num_out_of: Total number of Sockets on this `Socket Position`
        :type num_out_of: ``int``
        :return: Position of described Socket on the `QD_Node`
        :rtype: ``x, y``
        """
        x = self.socket_offsets[position] if (position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM)) else self.gfx.width + self.socket_offsets[position]

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # start from bottom
            y = self.gfx.height - self.gfx.edge_roundness - self.gfx.title_vertical_padding - index * self.socket_spacing
        elif position in (LEFT_CENTER, RIGHT_CENTER):
            num_sockets = num_out_of
            node_height = self.gfx.height
            top_offset = self.gfx.title_height + 2 * self.gfx.title_vertical_padding + self.gfx.edge_padding
            available_height = node_height - top_offset

            total_height_of_all_sockets = num_sockets * self.socket_spacing
            new_top = available_height - total_height_of_all_sockets

            # y = top_offset + index * self.socket_spacing + new_top / 2
            y = top_offset + available_height / 2.0 + (index - 0.5) * self.socket_spacing
            if num_sockets > 1:
                y -= self.socket_spacing * (num_sockets - 1) / 2

        elif position in (LEFT_TOP, RIGHT_TOP):
            # start from top
            y = self.gfx.title_height + self.gfx.title_vertical_padding + self.gfx.edge_roundness + index * self.socket_spacing
        else:
            # this should never happen
            y = 0

        return [x, y]

    def getSocketScenePosition(self, socket: 'Socket') -> '(x, y)':
        """
        Get absolute Socket position in the QD_Scene

        :param socket: `Socket` which position we want to know
        :return: (x, y) Socket's scene position
        """
        nodepos = self.gfx.pos()
        socketpos = self.getSocketPosition(socket.index, socket.position, socket.count_on_this_node_side)
        return (nodepos.x() + socketpos[0], nodepos.y() + socketpos[1])

    def updateConnectedEdges(self):
        """Recalculate (Refresh) positions of all connected `Edges`. Used for updating Graphics Edges"""
        for socket in self.inputs + self.outputs:
            # if socket.hasEdge():
            for edge in socket.edges:
                edge.updatePositions()

    def remove(self):
        """Safely remove this QD_Node
        """
        if confg.DEBUG:
            print("> Removing QD_Node", self)

        if confg.DEBUG:
            print(" - remove all edges from sockets")

        for socket in (self.inputs + self.outputs):
            # if socket.hasEdge():
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

        :return: ``True`` if `QD_Node` is marked as `Dirty`
        :rtype: ``bool``
        """
        return self._is_dirty

    def markDirty(self, new_value: bool = True):
        """Mark this `QD_Node` as `Dirty`. See :ref:`evaluation` for more

        :param new_value: ``True`` if this `QD_Node` should be `Dirty`. ``False`` if you want to un-dirty this `QD_Node`
        :type new_value: ``bool``
        """
        self._is_dirty = new_value
        if self._is_dirty:
            self.onMarkedDirty()

    def onMarkedDirty(self):
        """Called when this `QD_Node` has been marked as `Dirty`. This method is supposed to be overriden"""
        pass

    def markChildrenDirty(self, new_value: bool = True):
        """Mark all first level children of this `QD_Node` to be `Dirty`. Not this `QD_Node` it self. Not other descendants

        :param new_value: ``True`` if children should be `Dirty`. ``False`` if you want to un-dirty children
        :type new_value: ``bool``
        """
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)

    def markDescendantsDirty(self, new_value: bool = True):
        """Mark all children and descendants of this `QD_Node` to be `Dirty`. Not this `QD_Node` it self

        :param new_value: ``True`` if children and descendants should be `Dirty`. ``False`` if you want to un-dirty children and descendants
        :type new_value: ``bool``
        """
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)
            other_node.markChildrenDirty(new_value)

    def isInvalid(self) -> bool:
        """Is this node marked as `Invalid`?

        :return: ``True`` if `QD_Node` is marked as `Invalid`
        :rtype: ``bool``
        """
        return self._is_invalid

    def markInvalid(self, new_value: bool = True):
        """Mark this `QD_Node` as `Invalid`. See :ref:`evaluation` for more

        :param new_value: ``True`` if this `QD_Node` should be `Invalid`. ``False`` if you want to make this `QD_Node` valid
        :type new_value: ``bool``
        """
        self._is_invalid = new_value
        if self._is_invalid: self.onMarkedInvalid()

    def onMarkedInvalid(self):
        """Called when this `QD_Node` has been marked as `Invalid`. This method is supposed to be overriden"""
        pass

    def markChildrenInvalid(self, new_value: bool = True):
        """Mark all first level children of this `QD_Node` to be `Invalid`. Not this `QD_Node` it self. Not other descendants

        :param new_value: ``True`` if children should be `Invalid`. ``False`` if you want to make children valid
        :type new_value: ``bool``
        """
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)

    def markDescendantsInvalid(self, new_value: bool = True):
        """Mark all children and descendants of this `QD_Node` to be `Invalid`. Not this `QD_Node` it self

        :param new_value: ``True`` if children and descendants should be `Invalid`. ``False`` if you want to make children and descendants valid
        :type new_value: ``bool``
        """
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)
            other_node.markChildrenInvalid(new_value)


    def evalOperation(self, input1, input2):
        return 123


    def evalImplementation(self):
        i1 = self.getInput(0)
        i2 = self.getInput(1)

        if i1 is None or i2 is None:
            self.markInvalid()
            self.markDescendantsDirty()
            self.gfx.setToolTip("Connect all inputs")
            return None

        else:
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
        """Evaluate all children of this `QD_Node`"""
        for node in self.getChildrenNodes():
            node.eval()

    # traversing nodes functions

    def getChildrenNodes(self) -> 'List[QD_Node]':
        """
        Retreive all first-level children connected to this `QD_Node` `Outputs`

        :return: list of `Nodes` connected to this `QD_Node` from all `Outputs`
        :rtype: List[:class:`~nodeeditor.node.QD_Node`]
        """
        if self.outputs == []: return []
        other_nodes = []
        for ix in range(len(self.outputs)):
            for edge in self.outputs[ix].edges:
                other_node = edge.getOtherSocket(self.outputs[ix]).node
                other_nodes.append(other_node)
        return other_nodes

    def getInput(self, index: int = 0) -> ['QD_Node', None]:
        """
        Get the **first**  `QD_Node` connected to the  Input specified by `index`

        :param index: Order number of the `Input Socket`
        :type index: ``int``
        :return: :class:`~nodeeditor.node.QD_Node` which is connected to the specified `Input` or ``None`` if there is no connection of index is out of range
        :rtype: :class:`~nodeeditor.node.QD_Node` or ``None``
        """
        try:
            input_socket = self.inputs[index]
            if len(input_socket.edges) == 0: return None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node
        except Exception as e:
            utils.dumpExcept(e)
            return None

    def getInputWithSocket(self, index: int = 0) -> [('QD_Node', 'Socket'), (None, None)]:
        """Get the **first**  `QD_Node` connected to the Input specified by `index` and the connection `Socket`

        :param index: Order number of the `Input Socket`
        :type index: ``int``
        :return: Tuple containing :class:`~nodeeditor.node.QD_Node` and :class:`~nodeeditor.socket.Socket` which
            is connected to the specified `Input` or ``None`` if there is no connection of index is out of range
        :rtype: (:class:`~nodeeditor.node.QD_Node`, :class:`~nodeeditor.socket.Socket`)
        """
        try:
            input_socket = self.inputs[index]
            if len(input_socket.edges) == 0:
                return None, None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node, other_socket
        except Exception as e:
            utils.dumpExcept(e)
            return None, None

    def getInputWithSocketIndex(self, index: int = 0) -> ('QD_Node', int):
        """
        Get the **first**  `QD_Node` connected to the Input specified by `index` and the connection `Socket`

        :param index: Order number of the `Input Socket`
        :type index: ``int``
        :return: Tuple containing :class:`~nodeeditor.node.QD_Node` and :class:`~nodeeditor.socket.Socket` which
            is connected to the specified `Input` or ``None`` if there is no connection of index is out of range
        :rtype: (:class:`~nodeeditor.node.QD_Node`, int)
        """
        try:
            edge = self.inputs[index].edges[0]
            socket = edge.getOtherSocket(self.inputs[index])
            return socket.node, socket.index
        except IndexError:
            # print("EXC: Trying to get input with socket index %d, but none is attached to" % index, self)
            return None, None
        except Exception as e:
            utils.dumpExcept(e)
            return None, None

    def getInputs(self, index: int = 0) -> 'List[QD_Node]':
        """
        Get **all** `Nodes` connected to the Input specified by `index`

        :param index: Order number of the `Input Socket`
        :type index: ``int``
        :return: all :class:`~nodeeditor.node.QD_Node` instances which are connected to the specified `Input` or ``[]`` if there is no connection of index is out of range
        :rtype: List[:class:`~nodeeditor.node.QD_Node`]
        """
        ins = []
        for edge in self.inputs[index].edges:
            other_socket = edge.getOtherSocket(self.inputs[index])
            ins.append(other_socket.node)
        return ins

    def getOutputs(self, index: int = 0) -> 'List[QD_Node]':
        """Get **all** `Nodes` connected to the Output specified by `index`

        :param index: Order number of the `Output Socket`
        :type index: ``int``
        :return: all :class:`~nodeeditor.node.QD_Node` instances which are connected to the specified `Output` or ``[]`` if there is no connection of index is out of range
        :rtype: List[:class:`~nodeeditor.node.QD_Node`]
        """
        outs = []
        for edge in self.outputs[index].edges:
            other_socket = edge.getOtherSocket(self.outputs[index])
            outs.append(other_socket.node)
        return outs

    # serialization functions

    def serialize(self) -> OrderedDict:
        inputs = []
        outputs = []

        for socket in self.inputs:
            inputs.append(socket.serialize())

        for socket in self.outputs:
            outputs.append(socket.serialize())

        ser_content = self.content.serialize() if isinstance(self.content, QD_Serializable) else {}
        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('pos_x', self.gfx.scenePos().x()),
            ('pos_y', self.gfx.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs),
            ('content', ser_content),
            ('op_code', self.__class__.op_code), # added by @register_opnode
        ])

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        try:
            if restore_id:
                self.id = data['id']

            hashmap[data['id']] = self

            self.setPos(data['pos_x'], data['pos_y'])
            self.title = data['title']

            data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
            data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
            num_inputs = len(data['inputs'])
            num_outputs = len(data['outputs'])

            # print("> deserialize node,   num inputs:", num_inputs, "num outputs:", num_outputs)
            # utils.printObj(data)

            # possible way to do it is reuse existing sockets...
            # dont create new ones if not necessary

            for socket_data in data['inputs']:
                found = None
                for socket in self.inputs:
                    # print("\t", socket, socket.index, "=?", socket_data['index'])
                    if socket.index == socket_data['index']:
                        found = socket
                        break
                if found is None:
                    # print("deserialization of socket data has not found input socket with index:", socket_data['index'])
                    # print("actual socket data:", socket_data)
                    # we can create new socket for this
                    found = self.__class__.Socket_class(
                        node=self, index=socket_data['index'], position=socket_data['position'],
                        socket_type=socket_data['socket_type'], count_on_this_node_side=num_inputs,
                        is_input=True
                    )
                    self.inputs.append(found)  # append newly created input to the list
                found.deserialize(socket_data, hashmap, restore_id)

            for socket_data in data['outputs']:
                found = None
                for socket in self.outputs:
                    # print("\t", socket, socket.index, "=?", socket_data['index'])
                    if socket.index == socket_data['index']:
                        found = socket
                        break
                if found is None:
                    # print("deserialization of socket data has not found output socket with index:", socket_data['index'])
                    # print("actual socket data:", socket_data)
                    # we can create new socket for this
                    found = self.__class__.Socket_class(
                        node=self, index=socket_data['index'], position=socket_data['position'],
                        socket_type=socket_data['socket_type'], count_on_this_node_side=num_outputs,
                        is_input=False
                    )
                    self.outputs.append(found)  # append newly created output to the list
                found.deserialize(socket_data, hashmap, restore_id)

        except Exception as e:
            utils.dumpExcept(e)

        # also deseralize the content of the node
        # so far the rest was ok, now as last step the content...
        if isinstance(self.content, QD_Serializable):
            res = self.content.deserialize(data['content'], hashmap)
            return res

        return True
