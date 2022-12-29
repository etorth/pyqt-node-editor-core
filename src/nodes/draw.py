# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdopnode import *
from qdutils import *
from qdopnodecontentgfx import *


class _DrawContentGfx(QD_OpNodeContentGfx):
    def initUI(self):
        self.scene = QGraphicsScene()
        self.scene.addEllipse(0, 0, 30, 30, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.red))

        self.view = QGraphicsView()
        self.view.setScene(self.scene)

        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.box = QVBoxLayout(self)
        self.box.addWidget(self.view)


class _DrawContent(QD_OpNodeContent):
    NodeContentGfx_class =_DrawContentGfx


@utils.register_opnode
class _Draw(QD_OpNode):
    icon = "icons/editor.png"
    op_type = OPS_ACTION
    op_title = "绘图"

    NodeContent_class = _DrawContent


    def __init__(self, scene):
        super().__init__(scene, sockets={SocketType.In})
        self.eval()


    def evalImplementation(self):
        u_value = 1 # hack
        s_value = int(u_value)
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.gfx.setToolTip("")

        self.evalChildren()
        return self.value
