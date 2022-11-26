from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdnode import *
from qdutils import *
from qdnodecontentgfx import *


class _StateContentGfx_exit(QD_NodeContentGfx):
    def initUI(self):
        self.edit = QTextEdit()
        self.box = QVBoxLayout(self)
        self.box.setContentsMargins(0, 0, 0, 8)
        self.box.addWidget(self.edit)


class _StateContent_exit(QD_NodeContent):
    NodeContentGfx_class =_StateContentGfx_exit

    def serialize(self):
        res = super().serialize()
        res['value'] = self.gfx.edit.toPlainText()
        return res


    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.gfx.edit.setPlainText(value)
            return True & res
        except Exception as e:
            utils.dumpExcept(e)
        return res


@utils.register_opnode
class _State_exit(QD_Node):
    icon = "icons/editor.png"
    op_type = OPS_ACTION
    op_title = "退出分支"

    NodeContent_class = _StateContent_exit


    def __init__(self, scene):
        super().__init__(scene, sockets=[SocketType.In])
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
