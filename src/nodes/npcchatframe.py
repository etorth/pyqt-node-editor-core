# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdnode import *
from qdutils import *
from qdnodecontentgfx import *


class _NPCChatSelection(QWidget):
    def __init__(self, node: QD_Node, parent: QWidget = None):
        super().__init__(parent)

        self.node = node
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

        button_up.clicked.connect(self.onUpClicked)
        button_down.clicked.connect(self.onDownClicked)
        button_delete.clicked.connect(self.onDeleteClicked)

        vbox = QVBoxLayout()
        vbox.addWidget(button_up)
        vbox.addWidget(button_down)
        vbox.addWidget(button_delete)
        vbox.addWidget(QFrame())

        self.gbox.addLayout(vbox, 1, 1)


    def onUpClicked(self, checked: bool):
        index = self.node.content.gfx.editor.selections.indexOf(self)
        if index >= 1:
            self.node.content.gfx.editor.selections.removeWidget(self)
            self.node.content.gfx.editor.selections.insertWidget(index - 1, self)


    def onDownClicked(self, checked: bool):
        index = self.node.content.gfx.editor.selections.indexOf(self)
        if index >= 0 and index < self.node.content.gfx.editor.selections.count() - 1:
            self.node.content.gfx.editor.selections.removeWidget(self)
            self.node.content.gfx.editor.selections.insertWidget(index + 1, self)


    def onDeleteClicked(self, checked: bool):
        msgbox = QMessageBox()
        msgbox.setWindowTitle('删除对话选项')
        msgbox.setIcon(QMessageBox.Icon.Warning)
        msgbox.setText('确定要删除这个对话选项吗？')
        msgbox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msgbox.setDefaultButton(QMessageBox.StandardButton.No)
        ret = msgbox.exec()

        if ret == QMessageBox.StandardButton.Yes:
            self.node.content.gfx.editor.selections.removeWidget(self)
            self.deleteLater()

        self.node.content.gfx.editor.onChatOutputsChanged()


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
        selections_layout = self.layout().itemAt(1).layout()
        selections_layout.addWidget(_NPCChatSelection(selections_layout))


class _NPCChatFrameEditor(QSplitter):
    def __init__(self, node: QD_Node, parent: QWidget = None):
        super().__init__(parent)

        self.node = node
        self.initUI()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)


    def initUI(self):
        if 'CreateLeftPannel':
            left_pannel = QWidget()
            self.addWidget(left_pannel)

            left_pannel_layout = QVBoxLayout(left_pannel)
            left_pannel_layout.setSpacing(10)

            if 'CreateNPCSelector':
                left_pannel_layout.addWidget(QLabel('聊天对象'))

                npc_hbox = QHBoxLayout()
                left_pannel_layout.addLayout(npc_hbox)

                self.map = QComboBox()
                self.map.addItems(["道馆", "比奇省", "边境城市"])
                self.map.currentIndexChanged.connect(self.onNPCChanged)
                npc_hbox.addWidget(self.map)

                self.npc = QComboBox()
                self.npc.addItems(["张三", "李四", "王五"])
                self.npc.currentIndexChanged.connect(self.onNPCChanged)
                npc_hbox.addWidget(self.npc)

            if 'CreateChatContent':
                self.content = QTextEdit()
                left_pannel_layout.addWidget(QLabel('聊天内容'))
                left_pannel_layout.addWidget(self.content)

            if 'CreateChatComment':
                self.comment = QTextEdit()
                left_pannel_layout.addWidget(QLabel('节点注释'))
                left_pannel_layout.addWidget(self.comment)

        if 'CreateChatSelections':
            right_pannel = _NPCChatSelectionPannel()
            self.addWidget(right_pannel)

            right_pannel_layout = QVBoxLayout(right_pannel)
            right_pannel_layout.setSpacing(10)

            right_pannel_layout.addWidget(QLabel('选择分支'), 0)

            if 'InsertSelections':
                self.selections = QVBoxLayout()
                right_pannel_layout.addLayout(self.selections, 1)

                self.selections.addWidget(_NPCChatSelection(self.node))
                self.selections.addWidget(_NPCChatSelection(self.node))
                self.selections.addWidget(_NPCChatSelection(self.node))
                self.selections.addWidget(_NPCChatSelection(self.node))

            right_pannel_layout.addWidget(QFrame(), 1)


    def onNPCChanged(self, index: int):
        self.node.content.gfx.setText('与%s的%s对话' % (self.map.currentText(), self.npc.currentText()))


    def onChatOutputsChanged(self):
        self.node.content.gfx.setOutputs([SocketType.In] + [SocketType(index + SocketType.IndexOut_min()) for index in range(0, self.selections.count())])


class _NPCChatFrameContentGfx(QD_NodeContentGfx):
    def initUI(self):
        self.editor = None
        self.label = QLabel('NPC对话')

        self.box = QVBoxLayout(self)
        self.box.addWidget(self.label)


    def mouseDoubleClickEvent(self, event):
        self.editor = _NPCChatFrameEditor(self.node)
        subwin = utils.main_window.mdiArea.addSubWindow(self.editor)
        subwin.setWindowIcon(QIcon('.'))
        subwin.show()


    def setText(self, s: str):
        if not s:
            s = 'NPC对话'
        self.label.setText(s)


    def setOutputs(self, sockets):
        self.node.initSockets(sockets, True)


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
