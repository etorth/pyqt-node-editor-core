# -*- coding: utf-8 -*-
from qdutils import *
from qdserializable import *
from qdstateconfggfx import *


class QD_StateConfg(QD_Serializable):
    StateConfgGfx_class = QD_StateConfgGfx


    def __init__(self, parent: 'QWidget' = None):
        super().__init__()
        self.gfx = self.__class__.StateConfgGfx_class(parent)


    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('log', self.gfx.log.toPlainText()),
            ('comment', self.gfx.comment.toPlainText()),
            ('timeout', self.gfx.timeout.text()),
        ])


    def deserialize(self, data: dict) -> bool:
        self.gfx.log.setPlainText(data['log'])
        self.gfx.comment.setPlainText(data['comment'])
        self.gfx.timeout.setText(data['timeout'])
        return True
