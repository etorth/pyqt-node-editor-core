# -*- coding: utf-8 -*-
from collections import OrderedDict
from qdserializable import QD_Serializable
from PyQt6.QtWidgets import *


class NodeContentGfx(QWidget):
    def __init__(self, content: 'NodeContent', parent: QWidget = None):
        super().__init__(parent)

        self.content = content
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)


    def setEditingFlag(self, value: bool):
        self.content.node.scene.getView().editingFlag = value
