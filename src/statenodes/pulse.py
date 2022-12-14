# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdstatewidget import QD_StateWidget
from qdsocket import *
from qdutils import *
from qdstatenode import QD_StateNode
from qdstatenodegfx import QD_StateNodeGfx
import math


from qdutils import *


class _StateNodeGfx_pulse(QD_StateNodeGfx):
    def __init__(self, node: 'QD_StateNode', parent: QGraphicsItem = None):
        super().__init__(node, parent)

        self.hovered = False
        self._was_moved = False
        self._last_selected_state = False
        self.pulse_angle = 40

        self.initSizes()
        self.initAssets()
        self.initUI()


    @property
    def width(self) -> int:
        return self._rect_width


    @property
    def height(self) -> int:
        return self._rect_height


    def initUI(self):
        pass


    def initSizes(self):
        self._rect_width  = 80
        self._rect_height = 60
        self._rect_image_width  = 40
        self._rect_image_height = 40


    def initAssets(self):
        self._color = QColor("#7F000000")
        self._color_hovered = QColor("#FF37A6FF")
        self._color_selected = QColor("#FFF7862F")
        self._color_hover_selected = QColor("#FFFFA637")

        self._pen_default = QPen(self._color)
        self._pen_default.setWidthF(2.0)
        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(2.0)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_hovered.setWidthF(3.0)
        self._pen_hover_selected = QPen(self._color_hover_selected)
        self._pen_hover_selected.setWidthF(3.0)

        self._image = QImage("icons/pulse.png")


    def switchSocketPosition(self):
        self.pulse_angle *= -1
        self.node.updateSockets()
        self.update()


    def onSelected(self):
        self.node.scene.gfx.itemSelected.emit()


    def doSelect(self, new_state=True):
        self.setSelected(new_state)
        self._last_selected_state = new_state

        if new_state:
            self.onSelected()


    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        for node in self.scene().scene.nodes:
            if node.gfx.isSelected():
                node.updateConnectedEdges()
        self._was_moved = True


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
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


    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = True
        self.update()


    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = False
        self.update()


    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height).normalized()


    def paint(self, painter, option: QStyleOptionGraphicsItem, widget=None):
        path_content = QPainterPath()
        path_content.setFillRule(Qt.FillRule.WindingFill)
        path_content.addEllipse(QRectF(0, 0, self.width, self.height))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.playerColor()))
        painter.drawPath(path_content.simplified())

        path_outline = QPainterPath()
        path_outline.addEllipse(QRectF(-1, -1, self.width + 2, self.height + 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self.hovered:
            painter.setPen(self._pen_hover_selected if self.isSelected() else self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_selected if self.isSelected() else self._pen_default)
            painter.drawPath(path_outline.simplified())

        img_x = max(0, (self.width  - self._rect_image_width ) / 2)
        img_y = max(0, (self.height - self._rect_image_height) / 2)

        img_w = self.width  - 2 * img_x
        img_h = self.height - 2 * img_y

        utils.drawNodeStateIcon(painter, self.node.iconIndex, self.width / 2, 0, False)
        painter.drawImage(QRectF(img_x, img_y, img_w, img_h), self._image)


@utils.stateNodeRegister
class StateNode_pulse(QD_StateNode):
    stateName = '??????'
    StateNodeGfx_class = _StateNodeGfx_pulse
    def __init__(self, scene: 'QD_QuestScene', sockets: set = {SocketType.In, SocketType.Out_True, SocketType.PulseOut}):
        super().__init__(scene, sockets)


    def getSocketPosition(self, socktype: SocketType) -> QPointF:
        match socktype:
            case SocketType.In:
                return QPointF(0, self.gfx.height / 2)
            case SocketType.Out_True:
                return QPointF(self.gfx.width, self.gfx.height / 2)
            case SocketType.PulseOut:
                return QPointF(
                        self.gfx.width  / 2 * (1.0 + math.cos(math.radians(self.gfx.pulse_angle))),
                        self.gfx.height / 2 * (1.0 + math.sin(math.radians(self.gfx.pulse_angle))))
            case _:
                raise ValueError('Invalid socket type %d' % socktype)
