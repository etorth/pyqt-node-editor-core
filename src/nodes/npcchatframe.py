# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdnode import *
from qdutils import *
from qdnodecontentgfx import *


class _NPCChatSelection(QWidget):
    def __init__(self, layout: QBoxLayout, parent: QWidget = None):
        super().__init__(parent)

        self.in_layout = layout
        self.initUI()


    def initUI(self):
        self.gbox = QGridLayout(self)

        self.text = QLineEdit()
        self.gbox.addWidget(self.text, 0, 0)

        self.comment = QTextEdit()
        self.gbox.addWidget(self.comment, 1, 0)

        self.close = QCheckBox('关闭界面')
        self.gbox.addWidget(self.close, 0, 1)

        button_up     = QPushButton('上移选项')
        button_down   = QPushButton('下移选项')
        button_delete = QPushButton('删除选项')

        button_delete.clicked.connect(self.onDeleteClicked)

        vbox = QVBoxLayout()
        vbox.addWidget(button_up)
        vbox.addWidget(button_down)
        vbox.addWidget(button_delete)
        vbox.addWidget(QFrame())

        self.gbox.addLayout(vbox, 1, 1)


    def onDeleteClicked(self, checked: bool):
        msgbox = QMessageBox()
        msgbox.setWindowTitle('删除对话选项')
        msgbox.setIcon(QMessageBox.Icon.Warning)
        msgbox.setText('确定要删除这个对话选项吗？')
        msgbox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msgbox.setDefaultButton(QMessageBox.StandardButton.No)
        ret = msgbox.exec()

        if ret == QMessageBox.StandardButton.Yes:
            self.in_layout.removeWidget(self)
            self.deleteLater()


class _NPCChatSelectionPannel(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.actions = []
        self.initActions()


    def initActions(self):
        self.actions.append(QAction(QIcon('icons/state.png'), '添加状态', triggered=self.onAddNewSelection))


    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        for act in self.actions:
            context_menu.addAction(act)

        context_menu.exec(self.mapToGlobal(event.pos()))


    def onAddNewSelection(self):
        self.layout().insertWidget(self.layout().count() - 1, _NPCChatSelection(self.layout()), 1)


class _NPCChatFrameEditor(QSplitter):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.initUI()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)


    def initUI(self):
        if 'CreateChatNPC':
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(10)

            content_layout.addWidget(QLabel('聊天对象'))

            npc_hbox = QHBoxLayout()
            content_layout.addLayout(npc_hbox)

            self.map = QComboBox()
            self.map.addItems(["道馆", "比奇省", "边境城市"])
            npc_hbox.addWidget(self.map)

            self.npc = QComboBox()
            self.npc.addItems(["张三", "李四", "王五"])
            npc_hbox.addWidget(self.npc)

            self.content = QTextEdit()
            content_layout.addWidget(QLabel('聊天内容'))
            content_layout.addWidget(self.content)

            self.comment = QTextEdit()
            content_layout.addWidget(QLabel('节点注释'))
            content_layout.addWidget(self.comment)

            self.addWidget(content_widget)

        if 'CreateChatSelections':
            selection_widget = _NPCChatSelectionPannel()
            self.selection_layout = QVBoxLayout(selection_widget)

            self.selection_layout.setSpacing(10)
            self.selection_layout.addWidget(QLabel('选择分支'))

            self.selection_layout.addWidget(_NPCChatSelection(self.selection_layout), 1)
            self.selection_layout.addWidget(_NPCChatSelection(self.selection_layout), 1)
            self.selection_layout.addWidget(_NPCChatSelection(self.selection_layout), 1)
            self.selection_layout.addWidget(_NPCChatSelection(self.selection_layout), 1)

            self.selection_layout.addWidget(QFrame(), 1)

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
