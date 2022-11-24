# -*- coding: utf-8 -*-
from qdutils import *
from qdserializable import *
from qdstateconfggfx import *


class QD_StateConfg(QD_Serializable):
    StateConfgGfx_class = QD_StateConfgGfx


    def __init__(self, parent: 'QWidget' = None):
        super().__init__()
        self.gfx = self.__class__.StateConfgGfx_class(parent)

    def initUI(self):
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)

        self.splitter.addWidget(self.createLeftPannel())
        self.splitter.addWidget(self.createMiddlePannel())


    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('op_code', self.__class__.op_code), # added by @register_opnode
            ('log', self.gfx.log.toPlainText()),
            ('timeout', self.gfx.timeout.text()),
        ])


    def deserialize(self, data: dict) -> bool:
        self.gfx.log.setPlainText(data['log'])
        self.gfx.timeout.setText(data['timeout'])
        return True
