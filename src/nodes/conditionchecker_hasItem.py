# -*- coding: utf-8 -*-
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from qdopnode import *
from qdutils import *
from qdopnodecontentgfx import *


class _ConditionCheckerContentGfx_hasItem(QD_OpNodeContentGfx):
    def initUI(self):
        self.choice = QComboBox()
        self.choice.addItems(["大于", "小于", "等于", "不等于", "不大于", "不小于"])

        self.edit = QLineEdit()
        self.edit.setValidator(QIntValidator())
        self.edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.edit.editingFinished.connect(self.onEditingFinished)

        self.items = QComboBox()
        self.items.addItems(["太阳水", "龙纹剑", "幽灵战衣（男）", "金币"])

        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(10, 10, 10, 10)
        self.hbox.setSpacing(5)

        self.hbox.addWidget(QLabel('拥有'))
        self.hbox.addWidget(self.choice)
        self.hbox.addWidget(self.edit)
        self.hbox.addWidget(QLabel('件'))
        self.hbox.addWidget(self.items)


    def onEditingFinished(self):
        if self.content.node:
            if self.edit.text():
                if int(self.edit.text()) < 0:
                    self.content.node.markInvalid(True)
                    self.content.node.gfx.setToolTip('Invalid level integer')
                else:
                    self.content.node.markInvalid(False)
                    self.content.node.gfx.setToolTip('')
            else:
                self.content.node.markDirty(True)


class _ConditionCheckerContent_hasItem(QD_OpNodeContent):
    NodeContentGfx_class = _ConditionCheckerContentGfx_hasItem


    def serialize(self):
        data = super().serialize()
        data['choice'] = self.gfx.choice.currentIndex()
        data['value'] = self.gfx.edit.text()
        data['item'] = self.gfx.items.currentIndex()
        return data


    def deserialize(self, data, hashmap=None, restore_id: bool = True):
    def deserialize(self, data, hashmap={}, restore_id: bool = True):
        self.gfx.choice.setCurrentIndex(data['choice'])
        self.gfx.edit.setText(data['value'])
        self.gfx.items.setCurrentIndex(data['item'])
        return True


@utils.opNodeRegister
class _ConditionChecker_hasItem(QD_OpNode):
    icon = "icons/checker.png"
    op_type = OPS_CHECKER
    opTitle = "拥有物品"

    NodeContent_class = _ConditionCheckerContent_hasItem

    def __init__(self, scene):
        super().__init__(scene, sockets={SocketType.In, SocketType.Out_True, SocketType.Out_False})
        self.eval()


    def initInnerClasses(self):
        super().initInnerClasses()
        self.content.gfx.edit.textChanged.connect(self.onInputChanged)


    def evalImplementation(self):
        self.value = 12
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.gfx.setToolTip("")

        self.evalChildren()
        return self.value
