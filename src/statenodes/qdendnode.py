# -*- coding: utf-8 -*-
from PyQt6.QtCore import QPointF

from qdstatenodegfx import QD_StateNodeGfx
from qdstatewidget import QD_StateWidget
from qdsocket import *
from qdutils import *
from qdstatenode import QD_StateNode


class QD_EndNode(QD_StateNode):
    def __init__(self, scene: 'QD_QuestScene', sockets: set = {SocketType.In}):
        super().__init__(scene, sockets)
        self.title = '结束节点'
