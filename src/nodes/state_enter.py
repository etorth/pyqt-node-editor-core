# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdopnode import *
from qdutils import *
from qdopnodecontentgfx import *


class _StateContentGfx_enter(QD_OpNodeContentGfx):
    def initUI(self):
        self.label = QLabel('进入')
        self.box = QVBoxLayout(self)
        self.box.addWidget(self.label)


class _StateContent_enter(QD_OpNodeContent):
    NodeContentGfx_class =_StateContentGfx_enter

    def serialize(self):
        data = super().serialize()
        data['value'] = self.gfx.label.text()
        return data


    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        super().deserialize(data, hashmap, restore_id)
        return self.gfx.label.setText(data['value'])


@utils.opNodeRegister
class _State_enter(QD_OpNode):
    icon = "icons/editor.png"
    op_type = OPS_ACTION
    opTitle = "进入节点"

    NodeContent_class = _StateContent_enter


    def __init__(self, scene):
        super().__init__(scene, sockets=[SocketType.Out_True])
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
