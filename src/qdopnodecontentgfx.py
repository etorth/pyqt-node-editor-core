# -*- coding: utf-8 -*-
from qdserializable import QD_Serializable
from PySide6.QtWidgets import *


class QD_OpNodeContentGfx(QWidget):
    def __init__(self, content: 'QD_OpNodeContent', parent: QWidget = None):
        super().__init__(parent)

        self.content = content
        self.node = content.node

        self.resize(0, 0)
        self.initUI()

    def initUI(self):
        raise NotImplementedError()
