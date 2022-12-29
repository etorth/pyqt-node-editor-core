# -*- coding: utf-8 -*-

import math
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdutils import *


class QD_StateNodeGfx(QGraphicsObject):
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

    sizeChanged = pyqtSignal()

    def __init__(self, node: 'QD_StateNode', parent: QGraphicsItem = None):
        """
        :param node: reference to :class:`node.QD_OpNode`
        :type node: :class:`node.QD_OpNode`
        :param parent: parent widget
        :type parent: QWidget

        :Instance Attributes:

            - **node** - reference to :class:`node.QD_OpNode`
        """
        super().__init__(parent)
        self.node = node

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
        """title of this `QD_OpNode`

        :getter: current Graphics QD_OpNode title
        :setter: stores and make visible the new title
        :type: str
        """
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
        """Set up this ``QGraphicsItem``"""
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
        """Set up internal attributes like `width`, `height`, etc."""
        self._mini_width = 120
        self._mini_height = 100
        self._widget_margin = 5

        self._width = self._mini_width
        self._height = self._mini_height

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
        win = utils.main_window.findMdiChildByStateNode(self.node)
        if win:
            widget = win.widget()
            widget.confg.gfx.log.setText(self.edit.toPlainText())


    def onSelected(self):
        """Our event handling when the node was selected"""
        self.node.scene.gfx.itemSelected.emit()

    def doSelect(self, new_state=True):
        """Safe version of selecting the `Graphics QD_OpNode`. Takes care about the selection state flag used internally

        :param new_state: ``True`` to select, ``False`` to deselect
        :type new_state: ``bool``
        """
        self.setSelected(new_state)
        self._last_selected_state = new_state

        if new_state:
            self.onSelected()


    def updatePosAndSize(self, dx: float, dy: float, dw: float, dh: float):
        self.prepareGeometryChange()
        self.setPos(self.mousePressRect.topLeft() + QPointF(dx, dy))
        self._width = max(self.mousePressRect.width() + dw, self._mini_width)
        self._height = max(self.mousePressRect.height() + dh, self._mini_height)
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
            case self.handleTopLeft     : self.updatePosAndSize(dx, dy, -dx, -dy)
            case self.handleTopMiddle   : self.updatePosAndSize( 0, dy,   0, -dy)
            case self.handleTopRight    : self.updatePosAndSize( 0, dy,  dx, -dy)
            case self.handleMiddleLeft  : self.updatePosAndSize(dx,  0, -dx,   0)
            case self.handleMiddleRight : self.updatePosAndSize( 0,  0,  dx,   0)
            case self.handleBottomLeft  : self.updatePosAndSize(dx,  0, -dx,  dy)
            case self.handleBottomMiddle: self.updatePosAndSize( 0,  0,   0,  dy)
            case self.handleBottomRight : self.updatePosAndSize( 0,  0,  dx,  dy)
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
            if root.__class__.__name__ == 'QD_StartNode' and hasattr(root, 'index'):
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

        offset = 24.0
        if self.node.isDirty(): offset = 0.0
        if self.node.isInvalid(): offset = 48.0

        painter.drawImage(QRectF(-10, -10, 24.0, 24.0), self._icons, QRectF(offset, 0, 24.0, 24.0))
        painter.drawImage(QRectF(25, 20, 50, 50), self._image)
