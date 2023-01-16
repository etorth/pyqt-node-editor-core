# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdutils import *
from qdserdespod import *

class _RelationalComboBox_SerdesPod(QD_SerdesPod):
    def __init__(self, box):
        super().__init__()
        self.box = box


    def serialize(self) -> dict:
        return super().serialize() | {
            'index': self.box.currentIndex(),
        }


    def deserialize(self, data: dict, hashmap: dict = {}, restoreId: bool = True):
        super().deserialize(data, hashmap, restoreId)
        self.box.setCurrentIndex(data['index'])


class QD_RelationalComboBox(QComboBox):
    SerdesPod_class = _RelationalComboBox_SerdesPod

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.spd = self.__class__.SerdesPod_class(self)
        self.addItems(["大于", "小于", "等于", "不大于", "不小于", "不等于"])
