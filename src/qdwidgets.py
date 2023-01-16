# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


class QD_RelationalComboBox(QComboBox):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.addItems(["大于", "小于", "等于", "不大于", "不小于", "不等于"])


class QD_RelationalConditionHBoxLayout(QHBoxLayout):
    def __init__(self, label: str, parent: QWidget = None):
        super().__init__(parent)
        self.setContentsMargins(10, 10, 10, 10)
        self.setSpacing(5)

        self.choice = QD_RelationalComboBox()
        self.edit = QLineEdit()
        self.edit.setValidator(QIntValidator())
        self.edit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.addWidget(QLabel(label))
        self.addWidget(self.choice)
        self.addWidget(self.edit)
