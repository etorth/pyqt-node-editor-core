# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdopnode import *
from qdutils import *
from qdopnodecontentgfx import *


class _ContainerContentGfx_repeat(QD_OpNodeContentGfx):
    def initUI(self):
        self.choice = QComboBox()
        self.choice.addItems(["为真时", "为假时", "无论真假"])

        self.times = QLineEdit()
        self.times.setValidator(QIntValidator())
        self.times.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.times.editingFinished.connect(self.onEditingFinished)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(QLabel("当结果"))
        self.hbox.addWidget(self.choice)
        self.hbox.addWidget(QLabel("重复执行"))
        self.hbox.addWidget(self.times)
        self.hbox.addWidget(QLabel("次"))

        self.vbox = QVBoxLayout(self)
        self.vbox.addLayout(self.hbox)

        self.ops = QLabel('操作')
        self.vbox.addWidget(self.ops)


    def onEditingFinished(self):
        if self.times.text() and int(self.times.text()) <= 0:
            self.times.setText("无穷")


class _ContainerContent_repeat(QD_OpNodeContent):
    NodeContentGfx_class =_ContainerContentGfx_repeat


@utils.opNodeRegister
class _Container_repeat(QD_OpNode):
    icon = "icons/editor.png"
    op_type = OPS_CONTAINER
    opTitle = "重复"

    NodeContent_class = _ContainerContent_repeat


    def __init__(self, scene):
        super().__init__(scene, sockets={SocketType.In, SocketType.Out_True, SocketType.Out_False})
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
