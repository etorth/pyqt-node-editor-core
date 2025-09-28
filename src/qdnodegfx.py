# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QGraphicsObject, QGraphicsItem


class QD_NodeGfx(QGraphicsObject):
    def __init__(self, node: 'QD_Node', parent: QGraphicsItem = None):
        super().__init__(parent)
        self.node = node
