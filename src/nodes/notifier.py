# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdnode import *
from qdutils import *
from qdnodecontentgfx import *


class _NotifierContentGfx(QD_NodeContentGfx):
    def initUI(self):
        self.edit = QLineEdit()
        self.box = QHBoxLayout(self)
        self.box.addWidget(self.edit)


class _NotifierContent(QD_NodeContent):
    NodeContentGfx_class =_NotifierContentGfx

    def serialize(self):
        res = super().serialize()
        res['value'] = self.gfx.edit.text()
        return res


    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.gfx.edit.setText(value)
            return True & res
        except Exception as e:
            utils.dumpExcept(e)
        return res


@utils.register_opnode
class _Notifier(QD_Node):
    icon = "icons/editor.png"
    op_type = OPS_ACTION
    op_title = "通知消息"

    NodeContent_class = _NotifierContent


    def __init__(self, scene):
        super().__init__(scene, sockets=[SocketType.In, SocketType.Out_1])
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
