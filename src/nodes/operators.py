# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdopnode import *
from qdutils import *
from qdopnodecontentgfx import *

class _CalcNodeBaseContentGfx(QD_OpNodeContentGfx):
    def initUI(self):
        if self.content.node is None:
            self.label = QLabel('operator')
        else:
            self.label = QLabel(self.content.node.__class__.op_title)

        self.box = QHBoxLayout(self)
        self.box.setContentsMargins(10, 10, 10, 10)
        self.box.setSpacing(5)

        self.box.addWidget(self.label)


class _CalcNodeBaseContent(QD_OpNodeContent):
    NodeContentGfx_class = _CalcNodeBaseContentGfx


class _CalcNodeBase(QD_OpNode):
    op_type = OPS_COMMAND
    NodeContent_class = _CalcNodeBaseContent


    def __init__(self, scene):
        super().__init__(scene, sockets=[SocketType.In, SocketType.Out_True, SocketType.Out_False])
        self.eval()


@utils.register_opnode
class _CalcNode_add(_CalcNodeBase):
    icon = "icons/add.png"
    op_title = "加"


    def evalOperation(self, input1, input2):
        return 1


@utils.register_opnode
class _CalcNode_sub(_CalcNodeBase):
    icon = "icons/sub.png"
    op_title = "减"


    def evalOperation(self, input1, input2):
        return 1


@utils.register_opnode
class _CalcNode_mul(_CalcNodeBase):
    icon = "icons/mul.png"
    op_title = "乘"


    def evalOperation(self, input1, input2):
        return 1


@utils.register_opnode
class _CalcNode_div(_CalcNodeBase):
    icon = "icons/divide.png"
    op_title = "除"


    def evalOperation(self, input1, input2):
        return 1
