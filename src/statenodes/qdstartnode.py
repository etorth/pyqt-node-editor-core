# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdstatewidget import QD_StateWidget
from qdsocket import *
from qdutils import *
from qdstatenode import QD_StateNode


from qdutils import *


class _StartNodeGfx(QGraphicsItem):
    def __init__(self, node: 'QD_StateNode', parent: QGraphicsItem = None):
        super().__init__(parent)
        self.node = node

        self.hovered = False
        self._was_moved = False
        self._last_selected_state = False

        self.initSizes()
        self.initAssets()
        self.initUI()


    @property
    def width(self) -> int:
        return self._rect_radius


    @property
    def height(self) -> int:
        return self._rect_radius


    def initUI(self):
        """Set up this ``QGraphicsItem``"""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setAcceptHoverEvents(True)


    def initSizes(self):
        self._rect_radius = 60
        self._rect_image_radius = 59

        self._rect_text_width  = 20
        self._rect_text_height = 20


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

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        self._image = QImage("icons/src.png")

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
            self.node.scene.history.storeHistory("QD_Node moved", setModified=True)

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
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        img_x = max(0, (self.width  - self._rect_image_radius) / 2)
        img_y = max(0, (self.height - self._rect_image_radius) / 2)
        img_w = self.width  - 2 * img_x
        img_h = self.height - 2 * img_y
        painter.drawImage(QRectF(img_x, img_y, img_w, img_h), self._image)

        text_x = max(0, (self.width  - self._rect_text_width ) / 2)
        text_y = max(0, (self.height - self._rect_text_height) / 2)
        text_w = self.width  - 2 * text_x
        text_h = self.height - 2 * text_y
        painter.drawText(QRectF(text_x, text_y, text_w, text_h), Qt.AlignmentFlag.AlignCenter, "Start")

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

        if self.node.isDirty():
            utils.draw_node_state_icon(painter, 1, self.width / 2, 0, False)
        elif self.node.isInvalid():
            utils.draw_node_state_icon(painter, 2, self.width / 2, 0, False)
        else:
            utils.draw_node_state_icon(painter, 0, self.width / 2, 0, False)


class QD_StartNode(QD_StateNode):
    StateNodeGfx_class = _StartNodeGfx
    def __init__(self, scene: 'QD_QuestScene', sockets: set = {SocketType.Out_True}):
        super().__init__(scene, sockets)


    def getSocketPosition(self, socktype: SocketType) -> QPointF:
        assert socktype is SocketType.Out_True, socktype
        return QPointF(self.gfx.width, self.gfx.height / 2)
