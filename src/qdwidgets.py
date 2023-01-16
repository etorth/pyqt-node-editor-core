# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdutils import *

class QD_RelationalComboBox(QComboBox):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.addItems(["大于", "小于", "等于", "不大于", "不小于", "不等于"])
