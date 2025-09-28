# -*- coding: utf-8 -*-
from PySide6.QtCore import QPointF, Signal, Qt
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from qdstatewidget import QD_StateWidget
from qdsocket import *
from qdutils import *
from qdnode import QD_Node

import math
from qdutils import *
from qdnodegfx import QD_NodeGfx


class _StateNodeGfx_act(QD_NodeGfx):
    dragSensitiveDistance = 5.0

    handleTopLeft = 1
    handleTopMiddle = 2
    handleTopRight = 3
    handleMiddleLeft = 4
    handleMiddleRight = 5
    handleBottomLeft = 6
    handleBottomMiddle = 7
    handleBottomRight = 8

    handleCursors = {
        handleTopLeft: Qt.CursorShape.SizeFDiagCursor,
        handleTopMiddle: Qt.CursorShape.SizeVerCursor,
        handleTopRight: Qt.CursorShape.SizeBDiagCursor,
        handleMiddleLeft: Qt.CursorShape.SizeHorCursor,
        handleMiddleRight: Qt.CursorShape.SizeHorCursor,
        handleBottomLeft: Qt.CursorShape.SizeBDiagCursor,
        handleBottomMiddle: Qt.CursorShape.SizeVerCursor,
        handleBottomRight: Qt.CursorShape.SizeFDiagCursor,
    }

    sizeChanged = Signal()

    def __init__(self, node: 'StateNode_act', parent: QGraphicsItem = None):
        super().__init__(node, parent)

        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None

        # init our flags
        self.hovered = False
        self._was_moved = False
        self._last_selected_state = False

        self.initSizes()
        self.initAssets()
        self.initUI()


    @property
    def title(self):
        return self._title


    @title.setter
    def title(self, value):
        self._title = value


    @property
    def width(self) -> int:
        return self._width


    @property
    def height(self) -> int:
        return self._height


    def initUI(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

        # init title
        self.title = self.node.title
        self.proxy = QGraphicsProxyWidget(self)

        frameRect = self.getFrameRect(self.width, self.height)

        self.frame = QFrame()
        self.frame.setMinimumSize(frameRect.size().toSize())
        self.frame.setGeometry(frameRect.toRect())
        self.sizeChanged.connect(self.onSizeChanged)

        self.proxy.setWidget(self.frame)
        self.vbox = QVBoxLayout(self.frame)

        self.edit = QTextEdit()
        self.edit.textChanged.connect(self.onTextChanged)
        self.vbox.addWidget(self.edit)


    def initSizes(self):
        self._miniWidth = 120
        self._miniHeight = 100
        self._widget_margin = 5

        self._width = self._miniWidth
        self._height = self._miniHeight

        self.edge_roundness = 6
        self.title_height = 24

    def initAssets(self):
        self._color = QColor("#7F000000")
        self._color_text = QColor("#FFFFFFFF")
        self._color_hovered = QColor("#FF37A6FF")
        self._color_selected = QColor("#FFF7862F")
        self._color_hover_selected = QColor("#FFFFA637")

        self._pen = QPen(self._color)
        self._pen.setWidthF(2.0)
        self._pen_text = QPen(self._color_text)
        self._pen_text.setWidthF(2.0)
        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(2.0)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_hovered.setWidthF(3.0)
        self._pen_hover_selected = QPen(self._color_hover_selected)
        self._pen_hover_selected.setWidthF(3.0)

        self._brush_background = QBrush(QColor("#E3474747"))

        self._icons = QImage("icons/status_icons.png")
        self._image = QImage("icons/src.png")


    def getFrameRect(self, w: float, h: float) -> QRectF:
        return QRectF(self._widget_margin, self.title_height + self._widget_margin, max(w - self._widget_margin * 2, 0), max(h - self.title_height - self._widget_margin * 2, 0))


    def onSizeChanged(self):
        self.frame.setGeometry(*self.getFrameRect(self.width, self.height).toRect().getRect())


    def onTextChanged(self):
        win = utils.mainWindow.findMdiChildByStateNode(self.node)
        if win:
            widget = win.widget()
            widget.confg.gfx.log.setText(self.edit.toPlainText())


    def onSelected(self):
        self.node.scene.gfx.itemSelected.emit()

    def doSelect(self, new_state=True):
        self.setSelected(new_state)
        self._last_selected_state = new_state

        if new_state:
            self.onSelected()


    def updatePosAndSize(self, dx: float, dy: float, dw: float, dh: float, miniRectPos: QPointF):
        self.prepareGeometryChange()
        newRect = QRectF(self.mousePressRect.topLeft() + QPointF(dx, dy), self.mousePressRect.size() + QSizeF(dw, dh))

        self.setPos(min(miniRectPos.x(), newRect.x()), min(miniRectPos.y(), newRect.y()))
        self._width = max(newRect.width(), self._miniWidth)
        self._height = max(newRect.height(), self._miniHeight)

        self._was_moved = True
        self.node.updateSockets()
        self.sizeChanged.emit()
        self.update()


    def handleDragAt(self, point):
        b = self.boundingRect()
        if b.contains(point):
            for socktype in self.node.getSocketTypeSet():
                if QLineF(self.node.getSocketPosition(socktype), point).length() <= self.dragSensitiveDistance:
                    return None

            if QLineF(point, b.topLeft    ()).length() <= self.dragSensitiveDistance: return self.handleTopLeft
            if QLineF(point, b.topRight   ()).length() <= self.dragSensitiveDistance: return self.handleTopRight
            if QLineF(point, b.bottomLeft ()).length() <= self.dragSensitiveDistance: return self.handleBottomLeft
            if QLineF(point, b.bottomRight()).length() <= self.dragSensitiveDistance: return self.handleBottomRight

            if abs(point.x() - b.left  ()) <= self.dragSensitiveDistance: return self.handleMiddleLeft
            if abs(point.x() - b.right ()) <= self.dragSensitiveDistance: return self.handleMiddleRight
            if abs(point.y() - b.top   ()) <= self.dragSensitiveDistance: return self.handleTopMiddle
            if abs(point.y() - b.bottom()) <= self.dragSensitiveDistance: return self.handleBottomMiddle
        return None


    def interactiveResize(self, mousePos):
        dx = mousePos.x() - self.mousePressPos.x()
        dy = mousePos.y() - self.mousePressPos.y()

        match self.handleSelected:
            case self.handleTopLeft     : self.updatePosAndSize(dx, dy, -dx, -dy, self.mousePressRect.bottomRight() - QPointF(self._miniWidth, self._miniHeight))
            case self.handleTopMiddle   : self.updatePosAndSize( 0, dy,   0, -dy, self.mousePressRect.bottomLeft () - QPointF(              0, self._miniHeight))
            case self.handleTopRight    : self.updatePosAndSize( 0, dy,  dx, -dy, self.mousePressRect.bottomLeft () - QPointF(              0, self._miniHeight))
            case self.handleMiddleLeft  : self.updatePosAndSize(dx,  0, -dx,   0, self.mousePressRect.bottomRight() - QPointF(self._miniWidth, self._miniHeight))
            case self.handleMiddleRight : self.updatePosAndSize( 0,  0,  dx,   0, self.mousePressRect.topLeft    () - QPointF(              0,                0))
            case self.handleBottomLeft  : self.updatePosAndSize(dx,  0, -dx,  dy, self.mousePressRect.topRight   () - QPointF(self._miniWidth,                0))
            case self.handleBottomMiddle: self.updatePosAndSize( 0,  0,   0,  dy, self.mousePressRect.topRight   () - QPointF(self._miniWidth,                0))
            case self.handleBottomRight : self.updatePosAndSize( 0,  0,  dx,  dy, self.mousePressRect.topLeft    () - QPointF(              0,                0))
            case _: raise ValueError("Invalid selected handle", self.handleSelected)


    def mousePressEvent(self, event):
        self.handleSelected = self.handleDragAt(event.pos())
        if self.handleSelected:
            self.mousePressPos = event.scenePos()
            self.mousePressRect = QRectF(self.pos(), QSizeF(self.width, self.height))
        super().mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if self.handleSelected is None:
            super().mouseMoveEvent(event)
            for node in self.scene().scene.nodes:
                if node.gfx.isSelected():
                    node.updateConnectedEdges()
            self._was_moved = True
        else:
            self.interactiveResize(event.scenePos())


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.update()

        # handle when gfx moved
        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.storeHistory("QD_OpNode moved", setModified=True)

            self.node.scene.resetLastSelectedStates()
            self.doSelect()  # also trigger itemSelected when node was moved

            # we need to store the last selected state, because moving does also select the nodes
            self.node.scene._last_selected_items = self.node.scene.getSelectedItems()

            # now we want to skip storing selection
            return

        # handle when gfx was clicked on
        if self._last_selected_state != self.isSelected() or self.node.scene._last_selected_items != self.node.scene.getSelectedItems():
            self.node.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()


    def mouseDoubleClickEvent(self, event):
        self.node.onDoubleClicked(event)


    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = True
        self.update()


    def hoverMoveEvent(self, event):
        if self.isSelected():
            handle = self.handleDragAt(event.pos())
            if handle is None:
                cursor = Qt.CursorShape.ArrowCursor
            else:
                cursor = self.handleCursors[handle]
            self.setCursor(cursor)
        super().hoverMoveEvent(event)


    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        super().hoverLeaveEvent(event)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height).normalized()


    def playerColor(self) -> QColor:
        def normalizeLightness(color: QColor, lightness: float = 0.2) -> QColor:
            return color.lighter(round(lightness * 100 / color.lightnessF()))

        for root in self.node.getRoots():
            if root.__class__.__name__ == 'StateNode_enter' and hasattr(root, 'index'):
                return normalizeLightness(utils.player_color(root.index - 1))
        return normalizeLightness(QColor("#313131"))


    def paint(self, painter, option: QStyleOptionGraphicsItem, widget=None):
        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, self.edge_roundness, self.edge_roundness)
        path_title.addRect(0, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        path_title.addRect(self.width - self.edge_roundness, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.playerColor()))
        painter.drawPath(path_title.simplified())

        painter.setPen(self._pen_text)
        painter.drawText(QRectF(self.edge_roundness, 0, self.width - self.edge_roundness * 2, self.title_height), Qt.AlignmentFlag.AlignCenter, self.title)

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.FillRule.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(0, self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(self.width - self.edge_roundness, self.title_height, self.edge_roundness, self.edge_roundness)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(-1, -1, self.width + 2, self.height + 2, self.edge_roundness, self.edge_roundness)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self.hovered:
            painter.setPen(self._pen_hover_selected if self.isSelected() else self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_selected if self.isSelected() else self._pen)
            painter.drawPath(path_outline.simplified())

        utils.drawNodeStateIcon(painter, self.node.iconIndex, 0, 0, False)
        painter.drawImage(QRectF(25, 20, 50, 50), self._image)


@utils.stateNodeRegister
class StateNode_act(QD_Node):
    stateName = '情节'

    StateNodeWidget_class = QD_StateWidget
    StateNodeGfx_class = _StateNodeGfx_act

    icon = ""

    def __init__(self, scene: 'QD_QuestScene', sockets: set = {SocketType.In, SocketType.Out_True, SocketType.Out_False}):
        super().__init__(scene)
        self._title = '状态节点'

        # just to be sure, init these variables
        self.gfx = None
        self.sockets = []

        self.initInnerClasses()
        self.initSettings()

        self.scene.addNode(self)
        self.scene.gfx.addItem(self.gfx)

        self.pulse_on_bottom = True
        self.initSockets(sockets)

        # dirty and evaluation
        self._is_dirty = False
        self._is_invalid = False

        self.value = None
        self.markDirty(False)

    def __str__(self):
        return "<%s:%s %s..%s>" % (self._title, self.__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])

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

    def setPos(self, x: float, y: float):
        self.gfx.setPos(x, y)

    def initInnerClasses(self):
        self.gfx = self.__class__.StateNodeGfx_class(self)
        self.widget = self.__class__.StateNodeWidget_class(self)


    def initSettings(self):
        self._max_socket_in_spacing = 20
        self._max_socket_out_spacing = 30


    def initSockets(self, sockets, reset: bool = True):
        if reset:
            for sock in self.sockets:
                self.scene.gfx.removeItem(sock.gfx)
            self.sockets = []

        for type in sockets:
            self.sockets.append(self.__class__.Socket_class(node=self, socktype=type))

        self.updateSockets()


    def switchPulseSocketPosition(self):
        self.pulse_on_bottom = not self.pulse_on_bottom
        self.updateSockets()


    def onInputChanged(self, socket: 'QD_Socket'):
        self.markDirty(False)
        self.markDescendantsDirty()
        self.eval()


    def onDeserialized(self, data: dict):
        pass


    def onDoubleClicked(self, event):
        win = utils.mainWindow.findMdiChildByStateNode(self)
        if win:
            utils.mainWindow.mdiArea.setActiveSubWindow(win)
        else:
            subwin = utils.mainWindow.createMdiChild(self.widget)
            subwin.show()


    def doSelect(self, new_state: bool = True):
        self.gfx.doSelect(new_state)

    def isSelected(self):
        return self.gfx.isSelected()


    def getSocketScenePosition(self, socket: 'QD_Socket') -> QPointF:
        return self.gfx.pos() + self.getSocketPosition(socket.type)


    def addPulseIn(self):
        if self.getSocket(SocketType.PulseIn):
            return

        self.sockets.append(self.__class__.Socket_class(node=self, socktype=SocketType.PulseIn))
        self.updateSockets()


    def removePulseIn(self):
        for socket in self.sockets:
            if socket.type is SocketType.PulseIn:
                for edge in socket.edges:
                    if confg.DEBUG:
                        print("    - removing from socket:", socket, "edge:", edge)
                    edge.remove()
                self.scene.gfx.removeItem(socket.gfx)
                self.sockets.remove(socket)
        self.updateSockets()


    def isDirty(self) -> bool:
        return self._is_dirty

    # def markDirty(self, new_value: bool = True):
    #     self._is_dirty = new_value
    #     if self._is_dirty:
    #         self.onMarkedDirty()

    def onMarkedDirty(self):
        pass

    def markChildrenDirty(self, new_value: bool = True):
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)

    def markDescendantsDirty(self, new_value: bool = True):
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)
            other_node.markChildrenDirty(new_value)

    def getChildrenNodes(self) -> 'List[StateNode_act]':
        other_nodes = []
        for sock in self.sockets:
            if sock.is_output:
                for edge in sock.edges:
                    other_nodes.append(edge.getOtherSocket(sock).node)
        return other_nodes


    def serialize(self) -> dict:
        return {
            'id': self.id,
            'title': self._title,
            'position': (self.gfx.scenePos().x(), self.gfx.scenePos().y()),
            'sockets': [sock.serialize() for sock in self.sockets],
        }

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        try:
            if restore_id:
                self.id = data['id']

            hashmap[data['id']] = self

            self.setPos(*data['position'])
            self._title = data['title']

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
