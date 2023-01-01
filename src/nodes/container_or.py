# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdopnode import *
from qdutils import *
from qdopnodecontentgfx import *


class _ContainerContentGfx_or(QD_OpNodeContentGfx):
    def initUI(self):
        self.edit = QLineEdit(self)


class _ContainerContent_or(QD_OpNodeContent):
    NodeContentGfx_class =_ContainerContentGfx_or

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


@utils.opNodeRegister
class _Container_or(QD_OpNode):
    icon = "icons/editor.png"
    op_type = OPS_CONTAINER
    opTitle = "或"

    NodeContent_class = _ContainerContent_or


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
