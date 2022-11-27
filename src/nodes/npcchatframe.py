from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdnode import *
from qdutils import *
from qdnodecontentgfx import *


class _NPCChatFrameContentGfx(QD_NodeContentGfx):
    def initUI(self):
        self.label = QLabel('NPC对话')
        self.box = QVBoxLayout(self)
        self.box.addWidget(self.label)


    def mouseDoubleClickEvent(self, event):
        print('NPC对话框被双击了')


class _NPCChatFrameContent(QD_NodeContent):
    NodeContentGfx_class =_NPCChatFrameContentGfx

    def serialize(self):
        data = super().serialize()
        data['value'] = self.gfx.label.text()
        return data


    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        super().deserialize(data, hashmap, restore_id)
        return self.gfx.label.setText(data['value'])


@utils.register_opnode
class _NPCChatFrame(QD_Node):
    icon = "icons/editor.png"
    op_type = OPS_ACTION
    op_title = "NPC对话页"

    NodeContent_class = _NPCChatFrameContent


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
