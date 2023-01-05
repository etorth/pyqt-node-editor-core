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

    IndexOut_0 = 10
    IndexOut_1 = 11
    IndexOut_2 = 12
    IndexOut_3 = 13
    IndexOut_4 = 14
    IndexOut_5 = 15
    IndexOut_6 = 16
    IndexOut_7 = 17
    IndexOut_8 = 18
    IndexOut_9 = 19

    PulseIn = 100
    PulseOut = 101


    @staticmethod
    def IndexOut_min():
        return SocketType.IndexOut_0


    @staticmethod
    def IndexOut_max():
        return SocketType.IndexOut_9


    @property
    def is_in(self) -> bool:
        return self in (SocketType.In, SocketType.PulseIn)


    @property
    def is_out(self) -> bool:
        return not self.is_in


    @property
    def is_pulse(self) -> bool:
        return self in (SocketType.PulseIn, SocketType.PulseOut)


    @property
    def is_bool(self) -> bool:
        return self in (SocketType.Out_True, SocketType.Out_False)


    @property
    def as_bool(self) -> bool:
        if self is SocketType.Out_True:
            return True
        elif self is SocketType.Out_False:
            return False
        else:
            raise ValueError(self)


    @property
    def is_index(self) -> bool:
        return self >= SocketType.IndexOut_min() and self <= SocketType.IndexOut_max()


    @property
    def as_index(self) -> int:
        if self.is_index:
            return self - SocketType.IndexOut_min()
        else:
            raise ValueError(self)


    @property
    def cast_type(self):
        if self.is_bool:
            return bool
        elif self.is_index:
            return int
        else:
            raise ValueError(self)


class QD_SocketGfx(QGraphicsItem):
    def __init__(self, socket: 'QD_Socket'):
        super().__init__(socket.node.gfx)
        self.setAcceptHoverEvents(True)

        self.socket = socket
        self._hovered = False

        self.initSizes()
        self.initAssets()


    @property
    def color(self) -> QColor:
        return self.__class__.getSocketColor(self.socket.type)


    @property
    def radiusOutline(self) -> float:
        return self.radius + self._outlineWidth


    @property
    def radius(self) -> float:
        return self._normalRadius * (1.3 if self._hovered else 1.0)


    @staticmethod
    def getSocketColor(socktype: SocketType) -> QColor:
        match socktype:
            case SocketType.In:
                return QColor("#FF0056a6")
            case SocketType.Out_True:
                return QColor("#FF52e220")
            case SocketType.Out_False:
                return QColor("#FFf20316")
            case SocketType.PulseIn:
                return QColor("#FF2ac6a6")
            case SocketType.PulseOut:
                return QColor("#FF2af6a6")
            case _:
                min_r, max_r = 0.001, 0.700
                min_g, max_g = 0.500, 1.000
                min_b, max_b = 0.100, 0.300

                ratio = socktype.as_index / (SocketType.IndexOut_max() - SocketType.IndexOut_min())
                return QColor.fromRgbF(
                        min_r * ratio + max_r * (1.0 - ratio),
                        min_g * ratio + max_g * (1.0 - ratio),
                        min_b * ratio + max_b * (1.0 - ratio))


    def changeSocketType(self):
        self._brush = QBrush(self.color)
        self.update()


    def initSizes(self):
        self._outlineWidth = 1.0
        self._normalRadius = 6.0


    def initAssets(self):
        self._color_outline = QColor("#FF000000")
        self._color_highlighted = QColor("#FF37A6FF")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self._outlineWidth)

        self._pen_highlighted = QPen(self._color_highlighted)
        self._pen_highlighted.setWidthF(2.0)

        self._brush = QBrush(self.color)
        self._icon = QImage("icons/socket_pulse.png")


    def paint(self, painter, option: QStyleOptionGraphicsItem, widget=None):
        painter.setBrush(self._brush)
        painter.setPen(self._pen_highlighted if self._hovered else self._pen)
        painter.drawEllipse(QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius))
        if self.socket.type.is_pulse:
            painter.drawImage(QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius), self._icon)


    def boundingRect(self) -> QRectF:
        return QRectF(-self.radiusOutline, -self.radiusOutline, 2 * self.radiusOutline, 2 * self.radiusOutline)


    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        self._hovered = True
        self.prepareGeometryChange()
        self.update()


    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        self._hovered = False
        self.prepareGeometryChange()
        self.update()
