from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from statenodewidget import StateNodeWidget
from qdnode import *
from node_edge import EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER
from node_graphics_view import MODE_EDGE_DRAG  # , MODE_EDGES_REROUTING
from qdutils import *


class CalculatorSubWindow(StateNodeWidget):
    def __init__(self):
        super().__init__()
        # self.setAttribute(Qt.WA_DeleteOnClose)

        self.setTitle()

        self.initNewNodeActions()

        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.history.addHistoryRestoredListener(self.onHistoryRestored)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        self.scene.setNodeClassSelector(self.getNodeClassFromData)

        self.__closeEventListeners = []

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

    def fileLoad(self, filename):
        if super().fileLoad(filename):
            self.doEvalOutputs()
            return True

        return False

    def initNewNodeActions(self):
        self.node_actions = {}
        for node in utils.valid_node_types():
            self.node_actions[node.op_code] = QAction(QIcon(node.icon), node.op_title)
            self.node_actions[node.op_code].setData(node.op_code)

    def initNodesContextMenu(self):
        context_menu = QMenu(self)
        for type in utils.valid_node_types():
            context_menu.addAction(self.node_actions[type.op_code])
        return context_menu

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
            item = self.scene.getItemAt(event.pos())
            if confg.DEBUG:
                print(item)

            if type(item) == QGraphicsProxyWidget:
                item = item.widget()

            if hasattr(item, 'node') or hasattr(item, 'socket'):
                self.handleNodeContextMenu(event)
            elif hasattr(item, 'edge'):
                self.handleEdgeContextMenu(event)
            # elif item is None:
            else:
                self.handleNewNodeContextMenu(event)

            return super().contextMenuEvent(event)
        except Exception as e:
            utils.dumpExcept(e)

    def handleNodeContextMenu(self, event):
        if confg.DEBUG:
            print("CONTEXT: NODE")
        context_menu = QMenu(self)
        markDirtyAct = context_menu.addAction("Mark Dirty")
        markDirtyDescendantsAct = context_menu.addAction("Mark Descendant Dirty")
        markInvalidAct = context_menu.addAction("Mark Invalid")
        unmarkInvalidAct = context_menu.addAction("Unmark Invalid")
        evalAct = context_menu.addAction("Eval")

        addNodeMenu = context_menu.addMenu('Add QD_Node')
        addedActDict = {}
        for type in utils.valid_node_types():
            addedActDict[addNodeMenu.addAction(type.op_title)] = type

        action = context_menu.exec(self.mapToGlobal(event.pos()))
        if action is None:
            return

        selected = None
        item = self.scene.getItemAt(event.pos())

        if isinstance(item, QGraphicsProxyWidget):
            item = item.widget()

        if hasattr(item, 'node'):
            selected = item.node
        if hasattr(item, 'socket'):
            selected = item.socket.node

        if confg.DEBUG:
            print("got item:", selected)

        if selected and action == markDirtyAct:
            selected.markDirty()

        if selected and action == markDirtyDescendantsAct:
            selected.markDescendantsDirty()

        if selected and action == markInvalidAct:
            selected.markInvalid()

        if selected and action == unmarkInvalidAct:
            selected.markInvalid(False)

        if selected and action == evalAct:
            val = selected.eval()
            if confg.DEBUG:
                print("EVALUATED:", val)

        if selected:
            for addedAct in addedActDict.keys():
                if action == addedAct:
                    print("ADDING NODE: %s" % addedActDict[addedAct].op_title)
                    selected.addSubNode(addedActDict[addedAct])


    def handleEdgeContextMenu(self, event):
        if confg.DEBUG:
            print("CONTEXT: EDGE")
        context_menu = QMenu(self)
        bezierAct = context_menu.addAction("Bezier Edge")
        directAct = context_menu.addAction("Direct Edge")
        action = context_menu.exec(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.getItemAt(event.pos())
        if hasattr(item, 'edge'):
            selected = item.edge

        if selected and action == bezierAct: selected.edge_type = EDGE_TYPE_BEZIER
        if selected and action == directAct: selected.edge_type = EDGE_TYPE_DIRECT

    # helper functions
    def determine_target_socket_of_node(self, was_dragged_flag, new_calc_node):
        target_socket = None
        if was_dragged_flag:
            if len(new_calc_node.inputs) > 0: target_socket = new_calc_node.inputs[0]
        else:
            if len(new_calc_node.outputs) > 0: target_socket = new_calc_node.outputs[0]
        return target_socket

    def finish_new_node_state(self, new_calc_node):
        self.scene.doDeselectItems()
        new_calc_node.gfx.doSelect(True)
        new_calc_node.gfx.onSelected()

    def handleNewNodeContextMenu(self, event):
        if confg.DEBUG:
            print("CONTEXT: EMPTY SPACE")

        context_menu = self.initNodesContextMenu()
        action = context_menu.exec(self.mapToGlobal(event.pos()))

        if action is not None:
            new_calc_node = utils.get_class_from_opcode(action.data())(self.scene)
            scene_pos = self.scene.getView().mapToScene(event.pos())
            new_calc_node.setPos(scene_pos.x(), scene_pos.y())
            if confg.DEBUG:
                print("Selected node:", new_calc_node)

            if self.scene.getView().mode == MODE_EDGE_DRAG:
                # if we were dragging an edge...
                target_socket = self.determine_target_socket_of_node(self.scene.getView().drag_start_socket.is_output,
                                                                     new_calc_node)
                if target_socket is not None:
                    self.scene.getView().edgeDragEnd(target_socket.gfx)
                    self.finish_new_node_state(new_calc_node)

            else:
                self.scene.history.storeHistory("Created %s" % new_calc_node.__class__.__name__)
