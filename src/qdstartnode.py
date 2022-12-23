# -*- coding: utf-8 -*-
from PyQt6.QtCore import QPointF

from qdstatenodegfx import QD_StateNodeGfx
from qdstatewidget import QD_StateWidget
from qdsocket import *
from qdutils import *
from qdstatenode import QD_StateNode


class QD_StartNode(QD_StateNode):
    def __init__(self, scene: 'QD_QuestScene', sockets: set = {SocketType.Out_True}):
        super().__init__(scene, sockets)
        self.title = '开始节点'
