# -*- coding: utf-8 -*-
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *


class QD_RelationalComboBox(QComboBox):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.addItems(["大于", "小于", "等于", "不大于", "不小于", "不等于"])


    def fromDict(self, data: dict):
        self.setCurentIndex(data["index"])


    def toDict(self) -> dict:
        return {"index": self.currentIndex()}


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


    def fromDict(self, data: dict):
        self.choice.setCurrentIndex(data["index"])
        self.edit.setText(data["value"])


    def toDict(self) -> dict:
        return {
            "index": self.choice.currentIndex(),
            "value": self.edit.text()
        }
