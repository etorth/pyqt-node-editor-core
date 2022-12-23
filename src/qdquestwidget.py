# -*- coding: utf-8 -*-
import os
import json
from collections import OrderedDict

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdquestscene import *
from qdquestconfg import QD_QuestConfg
from qddraglistbox import QD_DragListBox
from qdstatenode import *
from qdpulsenode import *
from qdstartnode import *
from qdendnode import *
from qdedge import *
from qdviewgfx import MODE_EDGE_DRAG, QD_ViewGfx  # , MODE_EDGES_REROUTING
from qdutils import *


class QD_QuestWidget(QSplitter):
    Scene_class = QD_QuestScene
    StateNode_class = QD_StateNode
    StartNode_class = QD_StartNode
    EndNode_class = QD_EndNode
    InterruptNode_class = QD_PulseNode


    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.filename = None

        self.initUI()

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setTitle()
        self.initNewNodeActions()

        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.history.addHistoryRestoredListener(self.onHistoryRestored)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        self.scene.setNodeClassSelector(self.getNodeClassFromData)

        self.__closeEventListeners = []


    def initUI(self):
        self.confg = QD_QuestConfg()
        self.addWidget(self.confg.gfx)

        self.scene = self.__class__.Scene_class()
        self.view = QD_ViewGfx(self.scene.gfx)
        self.addWidget(self.view)

        self.setSizes([200, 800])


    def getNodeClassFromData(self, data):
        if 'op_code' not in data:
            return QD_Node
        return utils.get_class_from_opcode(data['op_code'])

    def doEvalOutputs(self):
        # eval all output nodes
        for node in self.scene.nodes:
            if node.__class__.__name__ == "CalcNode_Output":
                node.eval()

    def onHistoryRestored(self):
        self.doEvalOutputs()


    def fileNew(self):
        self.scene.clear()
        self.filename = None
        self.scene.history.clear()
        self.scene.history.storeInitialHistoryStamp()


    def fileLoad(self, filename: str):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            with open(filename, "r", encoding='utf-8') as f:
                data = json.load(f)

                if data['version'] != confg.APP_VERSION:
                    QMessageBox.warning(self, "Incompatible json file version: %s" % data['version'], "Current version is %s" % confg.APP_VERSION)
                    return False

                self.confg.deserialize(data['confg'])
                self.scene.deserialize(data['scene'])

                self.scene.has_been_modified = False
                self.scene.history.clear()
                self.scene.history.storeInitialHistoryStamp()

                self.filename = filename

                self.doEvalOutputs()
                return True

        except InvalidFile as e:
            QMessageBox.warning(self, "Error loading json file: %s" % filename, str(e))
            return False

        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid json file: %s" % filename, str(e))
            return False

        finally:
            QApplication.restoreOverrideCursor()


    def fileSave(self, filename: str = None):
        if filename is not None:
            self.filename = filename

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        with open(self.filename, "w", encoding='utf-8', newline='\n') as f:
            json.dump(self.serialize(), f, ensure_ascii=False, indent=4)
            print('saving to %s was successfull.' % self.filename)
            self.scene.has_been_modified = False

        QApplication.restoreOverrideCursor()
        return True

    def onAddNewStateNode(self):
        print("onAddNewStateNode")

    def onAddNewStateNode2(self):
        print("onAddNewStateNode2")


    def onAddNewInterruptNode(self):
        print("onAddNewInterruptNode")

    def initNewNodeActions(self):
        self.node_actions = []
        act = QAction(QIcon('icons/state.png'), '添加起始节点')
        act.node_type = self.__class__.StartNode_class
        self.node_actions.append(act)

        act = QAction(QIcon('icons/state.png'), '添加终止节点')
        act.node_type = self.__class__.EndNode_class
        self.node_actions.append(act)

        act = QAction(QIcon('icons/state.png'), '添加观察节点')
        act.node_type = self.__class__.InterruptNode_class
        self.node_actions.append(act)


        self.node_actions.append(QAction(QIcon('icons/state.png'), '添加状态节点', triggered=self.onAddNewStateNode))

    def createNodesContextMenu(self):
        context_menu = QMenu(self)
        for action in self.node_actions:
            context_menu.addAction(action)
        return context_menu

    def onAttrTimeoutEditingFinished(self):
        if self._attr_timeout_edit.text():
            if int(self._attr_timeout_edit.text()) < 0:
                self._attr_timeout_edit.setText("无限制")


    def isModified(self) -> bool:
        return self.scene.isModified()


    def isFilenameSet(self) -> bool:
        return self.filename is not None


    def getSelectedItems(self) -> list:
        return self.scene.getSelectedItems()

    def hasSelectedItems(self) -> bool:
        return self.getSelectedItems() != []


    def canUndo(self) -> bool:
        return self.scene.history.canUndo()


    def canRedo(self) -> bool:
        return self.scene.history.canRedo()

    def getUserFriendlyFilename(self) -> str:
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Quest"
        return name + ("*" if self.isModified() else "")


    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())

    def addCloseEventListener(self, callback):
        self.__closeEventListeners.append(callback)

    def closeEvent(self, event):
        for callback in self.__closeEventListeners:
            callback(self, event)

    def onDragEnter(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            # print(" ... denied drag enter event")
            event.setAccepted(False)

    def onDrop(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            eventData = event.mimeData().data(LISTBOX_MIMETYPE)
            dataStream = QDataStream(eventData, QIODevice.OpenModeFlag.ReadOnly)
            pixmap = QPixmap()
            dataStream >> pixmap
            op_code = dataStream.readInt()
            text = dataStream.readQString()

            mouse_position = event.position()
            scene_position = self.scene.gfx.views()[0].mapToScene(round(mouse_position.x()), round(mouse_position.y()))

            if confg.DEBUG:
                print("GOT DROP: [%d] '%s'" % (op_code, text), "mouse:", mouse_position, "scene:", scene_position)

            try:
                node = utils.get_class_from_opcode(op_code)(self.scene)
                node.setPos(scene_position.x(), scene_position.y())
                self.scene.history.storeHistory("Created node %s" % node.__class__.__name__)
            except Exception as e:
                utils.dumpExcept(e)

            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
        else:
            # print(" ... drop ignored, not requested format '%s'" % LISTBOX_MIMETYPE)
            event.ignore()

    def contextMenuEvent(self, event):
        try:
            item = self.scene.getItemAt(event.pos() - self.view.pos())
            if confg.DEBUG:
                print(item)

            if type(item) == QGraphicsProxyWidget:
                item = item.widget()

            if hasattr(item, 'node') or hasattr(item, 'socket'):
                self.handleNodeContextMenu(item.node, event)
            elif hasattr(item, 'edge'):
                self.handleEdgeContextMenu(event)
            # elif item is None:
            else:
                self.handleNewNodeContextMenu(event)

            return super().contextMenuEvent(event)
        except Exception as e:
            utils.dumpExcept(e)


    def onAddPulseInSocket(self, node):
        def doAddPulseInSocket():
            node.addPulseIn()
        return doAddPulseInSocket


    def onDeletePulseInSocket(self, node):
        def doDeletePulseInSocket():
            node.removePulseIn()
        return doDeletePulseInSocket


    def handleNodeContextMenu(self, node, event):
        if confg.DEBUG:
            print("CONTEXT: NODE")
        context_menu = QMenu(self)
        markDirtyAct = context_menu.addAction("Mark Dirty")
        markDirtyDescendantsAct = context_menu.addAction("Mark Descendant Dirty")
        markInvalidAct = context_menu.addAction("Mark Invalid")
        unmarkInvalidAct = context_menu.addAction("Unmark Invalid")
        evalAct = context_menu.addAction("Eval")

        if SocketType.PulseIn in node.getSocketTypeSet():
            context_menu.addAction("Delete Pulse Input Socket").triggered.connect(self.onDeletePulseInSocket(node))
        else:
            context_menu.addAction("Add Pulse Input Socket").triggered.connect(self.onAddPulseInSocket(node))

        addNodeMenu = context_menu.addMenu('Add Node')
        addedActDict = {}
        for type in utils.valid_node_types():
            addedActDict[addNodeMenu.addAction(type.op_title)] = type

        action = context_menu.exec(self.mapToGlobal(event.pos()))
        if action is None:
            return

        selected = None
        item = self.scene.getItemAt(event.pos() - self.view.pos())

        if isinstance(item, QGraphicsProxyWidget):
            item = item.widget()

        if hasattr(item, 'node'):
            selected = item.node

        if hasattr(item, 'socket'):
            selected = item.socket.node

        if confg.DEBUG:
            print("got item:", selected)

        if selected:
            if action == markDirtyAct:
                selected.markDirty()

            elif action == markDirtyDescendantsAct:
                selected.markDescendantsDirty()

            elif action == markInvalidAct:
                selected.markInvalid()

            elif action == unmarkInvalidAct:
                selected.markInvalid(False)

            elif action == evalAct:
                val = selected.eval()
                if confg.DEBUG:
                    print("EVALUATED:", val)

            else:
                for addedAct in addedActDict.keys():
                    if action == addedAct:
                        print("ADDING NODE: %s" % addedActDict[addedAct].op_title)
                        selected.addSubNode(addedActDict[addedAct])
                        break


    def handleEdgeContextMenu(self, event):
        if confg.DEBUG:
            print("CONTEXT: EDGE")
        context_menu = QMenu(self)
        bezierAct = context_menu.addAction("Bezier QD_Edge")
        directAct = context_menu.addAction("Direct QD_Edge")
        action = context_menu.exec(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.getItemAt(event.pos())
        if hasattr(item, 'edge'):
            selected = item.edge

        if selected and action == bezierAct: selected.edge_type = EdgeType.Bezier
        if selected and action == directAct: selected.edge_type = EdgeType.Direct

    # helper functions
    def determine_target_socket_of_node(self, was_dragged_flag, new_calc_node):
        target_socket = None
        if was_dragged_flag:
            if new_calc_node.getSocket(SockType.In):
                target_socket = new_calc_node.getSocket(SockType.In)
        else:
            if new_calc_node.getSocket(SockType.Out_1):
                target_socket = new_calc_node.getSocket(SockType.Out_1)
            elif new_calc_node.getSocket(SockType.Out_0):
                target_socket = new_calc_node.getSocket(SockType.Out_0)
        return target_socket

    def finish_new_node_state(self, new_calc_node):
        self.scene.doDeselectItems()
        new_calc_node.gfx.doSelect(True)
        new_calc_node.gfx.onSelected()

    def handleNewNodeContextMenu(self, event):
        if confg.DEBUG:
            print("CONTEXT: EMPTY SPACE in QS_QuestWidget")

        context_menu = self.createNodesContextMenu()
        action = context_menu.exec(self.mapToGlobal(event.pos()))

        if action is not None:
            if hasattr(action, 'node_type'):
                new_node_type = action.node_type
            else:
                new_node_type = self.__class__.StateNode_class

            print(action, 'in QD_QuestWidget')
            new_state_node = new_node_type(self.scene)
            scene_pos = self.scene.getView().mapToScene(event.pos() - self.view.pos())
            new_state_node.setPos(scene_pos.x(), scene_pos.y())
            if confg.DEBUG:
                print("Selected node:", new_state_node)

            # if self.scene.getView().mode == MODE_EDGE_DRAG:
            #     # if we were dragging an edge...
            #     target_socket = self.determine_target_socket_of_node(self.scene.getView().drag_start_socket.is_output, new_calc_node)
            #     if target_socket is not None:
            #         self.scene.getView().edgeDragEnd(target_socket.gfx)
            #         self.finish_new_node_state(new_calc_node)
            #
            # else:
            #     self.scene.history.storeHistory("Created %s" % new_calc_node.__class__.__name__)


    def addNodes(self):
        node1 = QD_Node(self.scene, "My Awesome QD_Node 1", sockets={SocketType.In, SocketType.Out_True, SocketType.Out_False})
        node2 = QD_Node(self.scene, "My Awesome QD_Node 2", sockets={SocketType.In, SocketType.Out_True, SocketType.Out_False})
        node3 = QD_Node(self.scene, "My Awesome QD_Node 3", sockets={SocketType.In, SocketType.Out_True, SocketType.Out_False})
        node1.setPos(-350, -250)
        node2.setPos(-75, 0)
        node3.setPos(200, -200)

        edge1 = QD_Edge(self.scene, node1.getSocket(SocketType.Out_True), node2.getSocket(SocketType.In), edge_type=EdgeType.Bezier)
        edge2 = QD_Edge(self.scene, node2.getSocket(SocketType.Out_True), node3.getSocket(SocketType.In), edge_type=EdgeType.Bezier)
        edge3 = QD_Edge(self.scene, node1.getSocket(SocketType.Out_True), node3.getSocket(SocketType.In), edge_type=EdgeType.Bezier)

        self.scene.history.storeInitialHistoryStamp()


    def addCustomNode(self):
        from qdnodecontent import QD_NodeContent
        from qdserializable import QD_Serializable

        class NNodeContent(QLabel):  # , QD_Serializable):
            def __init__(self, node, parent=None):
                super().__init__("FooBar")
                self.node = node
                self.setParent(parent)

        class NNode(QD_Node):
            NodeContent_class = NNodeContent

        self.scene.setNodeClassSelector(lambda data: NNode)
        node = NNode(self.scene, "A Custom QD_Node 1", sockets={SocketType.In, SocketType.Out_True, SocketType.Out_False})

        print("node content:", node.content)


    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('version', confg.APP_VERSION),
            ('confg', self.confg.serialize()),
            ('scene', self.scene.serialize()),
        ])


    def addDebugContent(self):
        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.black)
        outlinePen.setWidth(2)

        rect = self.gfx.addRect(-100, -100, 80, 100, outlinePen, greenBrush)
        rect.setFlag(QGraphicsItem.ItemIsMovable)

        text = self.gfx.addText("This is my Awesome text!", QFont("Ubuntu"))
        text.setFlag(QGraphicsItem.ItemIsSelectable)
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setDefaultTextColor(QColor.fromRgbF(1.0, 1.0, 1.0))

        widget1 = QPushButton("Hello World")
        proxy1 = self.gfx.addWidget(widget1)
        proxy1.setFlag(QGraphicsItem.ItemIsMovable)
        proxy1.setPos(0, 30)

        widget2 = QTextEdit()
        proxy2 = self.gfx.addWidget(widget2)
        proxy2.setFlag(QGraphicsItem.ItemIsSelectable)
        proxy2.setPos(0, 60)

        line = self.gfx.addLine(-200, -200, 400, -100, outlinePen)
        line.setFlag(QGraphicsItem.ItemIsMovable)
        line.setFlag(QGraphicsItem.ItemIsSelectable)
