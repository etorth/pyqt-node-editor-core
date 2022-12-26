# -*- coding: utf-8 -*-
from qdutils import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


class QD_BaseStateNodeGfx(QGraphicsObject):

    def __init__(self, node: 'QD_BaseStateNode', parent: QGraphicsItem = None):
        super().__init__(parent)
        self.node = node

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setAcceptHoverEvents(True)


    @property
    def width(self) -> int:
        raise NotImplementedError()


    @property
    def height(self) -> int:
        raise NotImplementedError()


    def mouseDoubleClickEvent(self, event):
        self.node.popMdiWindow()


    def boundingRect(self) -> QRectF:
        raise NotImplementedError()


    def playerColor(self) -> QColor:
        for root in self.node.getRoots():
            if root.__class__.__name__ == 'QD_StartNode' and hasattr(root, 'index'):
                return utils.player_color(root.index)
        return QColor("#313131")
