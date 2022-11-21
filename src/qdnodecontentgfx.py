# -*- coding: utf-8 -*-
from collections import OrderedDict
from qdserializable import QD_Serializable
from PyQt6.QtWidgets import *


class QD_NodeContentGfx(QWidget):
    def __init__(self, content: 'QD_NodeContent', parent: QWidget = None):
        super().__init__(parent)

        self.content = content
        self.resize(200, 50)
        self.initUI()

    def initUI(self):
        raise NotImplementedError()


    def setEditingFlag(self, value: bool):
        self.content.node.scene.getView().editingFlag = value
