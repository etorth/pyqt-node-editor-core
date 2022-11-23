from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdnode import *
from qdutils import *
from qdnodecontentgfx import *


class _StateContentGfx_enter(QD_NodeContentGfx):
    def initUI(self):
        self.label = QLabel('进入')
        self.box = QVBoxLayout(self)
        self.box.addWidget(self.label)


class _StateContent_enter(QD_NodeContent):
    NodeContentGfx_class =_StateContentGfx_enter

    def serialize(self):
        data = super().serialize()
        data['value'] = self.gfx.label.text()
        data['op_code'] = self.__class__.op_code
        return data


    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        super().deserialize(data, hashmap, restore_id)
        return self.gfx.label.setText(data['value'])


@utils.register_opnode
class _State_enter(QD_Node):
    icon = "icons/editor.png"
    op_type = OPS_ACTION
    op_title = "进入节点"

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
