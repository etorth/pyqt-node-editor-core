# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdnode import *
from qdutils import *
from qdnodecontentgfx import *


class _NPCChatSelection(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.initUI()


    def initUI(self):
        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout()

        self.text = QLineEdit()
        self.close = QCheckBox('关闭界面')

        hbox.addWidget(self.text)
        hbox.addWidget(self.close)

        vbox.addLayout(hbox)

        self.comment = QTextEdit()
        vbox.addWidget(self.comment)

class _NPCChatFrameEditor(QSplitter):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.initUI()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)


    def initUI(self):
        if 'CreateChatContent':
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(10)

            self.content = QTextEdit()
            content_layout.addWidget(QLabel('聊天内容'))
            content_layout.addWidget(self.content)

            self.comment = QTextEdit()
            content_layout.addWidget(QLabel('节点注释'))
            content_layout.addWidget(self.comment)

            self.addWidget(content_widget)

        if 'CreateChatSelections':
            selection_widget = QWidget()
            content_layout = QVBoxLayout(selection_widget)

            content_layout.setSpacing(10)
            content_layout.addWidget(QLabel('选择分支'))

            content_layout.addWidget(_NPCChatSelection())
            content_layout.addWidget(_NPCChatSelection())
            content_layout.addWidget(_NPCChatSelection())
            content_layout.addWidget(_NPCChatSelection())

            self.addWidget(selection_widget)


class _NPCChatFrameContentGfx(QD_NodeContentGfx):
    def initUI(self):
        self.label = QLabel('NPC对话')
        self.box = QVBoxLayout(self)
        self.box.addWidget(self.label)


    def mouseDoubleClickEvent(self, event):
        chateditor = _NPCChatFrameEditor()
        subwin = utils.main_window.mdiArea.addSubWindow(chateditor)
        subwin.setWindowIcon(QIcon('.'))
        subwin.show()


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
        super().__init__(scene, sockets=[SocketType.In, SocketType.Out_True])
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
