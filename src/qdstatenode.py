# -*- coding: utf-8 -*-
from PyQt6.QtCore import QPointF

from qdstatenodegfx import QD_StateNodeGfx
from qdstatewidget import QD_StateWidget
from qdsocket import *
from qdutils import *
from qdnode import QD_Node

import math
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdutils import *
from qdnodegfx import QD_NodeGfx


class QD_StateNode(QD_Node):
    StateNodeGfx_class = None

    def __init__(self, scene: 'QD_QuestScene', sockets: set = {SocketType.In, SocketType.Out_True, SocketType.Out_False}):
        super().__init__(scene)

        if self.__class__.StateNodeGfx_class is None:
            raise NotImplementedError("QD_StateNode::StateNodeGfx_class not defined")

        self.gfx = self.__class__.StateNodeGfx_class(self)

        self.scene.addNode(self)
        self.scene.gfx.addItem(self.gfx)

        self.sockets = []
        self.initSockets(sockets)


    def initSockets(self, sockets, reset: bool = True):
        if reset:
            for sock in self.sockets:
                self.scene.gfx.removeItem(sock.gfx)
            self.sockets = []

        for type in sockets:
            self.sockets.append(self.__class__.Socket_class(node=self, socktype=type))

        self.updateSockets()


    def updateSockets(self):
        for sock in self.sockets:
            sock.updateSocketPosition()


    def setPos(self, x: float, y: float):
        self.gfx.setPos(x, y)
