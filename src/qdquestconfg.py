# -*- coding: utf-8 -*-
from qdutils import *
from qdserializable import *
from qdquestconfggfx import *


class QD_QuestConfg(QD_Serializable):
    QuestConfgGfx_class = QD_QuestConfgGfx


    def __init__(self, parent: 'QWidget' = None):
        super().__init__()
        self.gfx = self.__class__.QuestConfgGfx_class(parent)


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
