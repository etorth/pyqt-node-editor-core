# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdnode import *
from qdutils import *
from qdnodecontentgfx import *


class _ConditionCheckerContentGfx_level(QD_OpNodeContentGfx):
    def initUI(self):
        self.choice = QComboBox()
        self.choice.addItems(["大于", "小于", "等于", "不等于", "不大于", "不小于"])

        self.edit = QLineEdit()
        self.edit.setValidator(QIntValidator())
        self.edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.edit.editingFinished.connect(self.onEditingFinished)

        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(10, 10, 10, 10)
        self.hbox.setSpacing(5)

        self.hbox.addWidget(QLabel('等级'))
        self.hbox.addWidget(self.choice)
        self.hbox.addWidget(self.edit)


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


class _ConditionCheckerContent_level(QD_OpNodeContent):
    NodeContentGfx_class = _ConditionCheckerContentGfx_level


    def serialize(self):
        data = super().serialize()
        data['choice'] = self.gfx.choice.currentIndex()
        data['value'] = self.gfx.edit.text()
        return data


    def deserialize(self, data, hashmap={}, restore_id: bool = True):
        super().deserialize(data, hashmap)
        self.gfx.edit.setText(data['value'])
        self.gfx.choice.setCurrentIndex(data['choice'])
        return True


@utils.register_opnode
class _ConditionChecker_level(QD_OpNode):
    icon = "icons/checker.png"
    op_type = OPS_CHECKER
    op_title = "等级"

    NodeContent_class = _ConditionCheckerContent_level

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
