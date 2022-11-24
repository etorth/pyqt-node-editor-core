# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from qdutils import *

class QD_StateConfgGfx(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.log = None
        self.timeout = None

        self.initUI()


    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

        if "CreateStateNodeLogWidgets":
            self.log = QTextEdit()

            self.layout.addWidget(QLabel("节点日志"))
            self.layout.addWidget(self.log)

        if "CreateStateNodeTimeoutWidgets":
            timeout_layout = QHBoxLayout()
            timeout_layout.setSpacing(5)

            self.timeout = QLineEdit()
            self.timeout.setValidator(QIntValidator())
            self.timeout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.timeout.editingFinished.connect(self.onAttrTimeoutEditingFinished)

            self._attr_timeout_units = QComboBox()
            self._attr_timeout_units.addItems(["秒", "分钟", "小时", "天", "周", "月", "年"])

            timeout_layout.addWidget(QLabel("状态限时"))
            timeout_layout.addWidget(self.timeout)
            timeout_layout.addWidget(self._attr_timeout_units)

            self.layout.addLayout(timeout_layout)


    def onAttrTimeoutEditingFinished(self):
        if self.timeout.text():
            if int(self.timeout.text()) <= 0:
                self.timeout.setText("无限制")
