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

        if "CreateStateNodeLogWidgets":
            log_layout = QHBoxLayout()

            log_label = QLabel("节点日志")
            log_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

            self.log = QTextEdit()
            self.log.setMaximumHeight(200)

            log_layout.addWidget(log_label)
            log_layout.addWidget(self.log)

            self.layout.addLayout(log_layout)

        if "CreateStateNodeTimeoutWidgets":
            timeout_layout = QHBoxLayout()

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
            if int(self.timeout.text()) < 0:
                self.timeout.setText("无限制")
