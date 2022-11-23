# -*- coding: utf-8 -*-
from enum import Enum, unique
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

@unique
class SocketType(int, Enum):
    In = 0
    Out_True = 1
    Out_False = 2

    @property
    def is_In(self) -> bool:
        return self is SocketType.In

    def is_Out(self) -> bool:
        return self is SocketType.Out_True or self is SocketType.Out_False

class QD_SocketGfx(QGraphicsItem):
    def __init__(self, socket: 'QD_Socket'):
        super().__init__(socket.node.gfx)

        self.socket = socket
        self.is_highlighted = False

        self.radius = 6.0
        self.outline_width = 1.0

        self.initAssets()

    @property
    def color(self) -> QColor:
        return self.__class__.getSocketColor(self.socket.type)

    @property
    def radius_outline(self) -> float:
        return self.radius + self.outline_width

    @staticmethod
    def getSocketColor(socktype: SocketType) -> QColor:
        match socktype:
            case SocketType.In       : return QColor("#FF0056a6")
            case SocketType.Out_True : return QColor("#FF52e220")
            case SocketType.Out_False: return QColor("#FFf20316")
            case                    _: raise ValueError("Unknown socktype %s" % socktype)

    def changeSocketType(self):
        self._brush = QBrush(self.color)
        self.update()

    def initAssets(self):
        self._color_outline = QColor("#FF000000")
        self._color_highlighted = QColor("#FF37A6FF")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)

        self._pen_highlighted = QPen(self._color_highlighted)
        self._pen_highlighted.setWidthF(2.0)

        self._brush = QBrush(self.color)

    def paint(self, painter, option: QStyleOptionGraphicsItem, widget=None):
        painter.setBrush(self._brush)
        painter.setPen(self._pen_highlighted if self.is_highlighted else self._pen)
        painter.drawEllipse(QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius))

    def boundingRect(self) -> QRectF:
        return QRectF(-self.radius_outline, -self.radius_outline, 2 * self.radius_outline, 2 * self.radius_outline)
