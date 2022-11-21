# -*- coding: utf-8 -*-
"""A module containing Graphics representation of a :class:`~nodeeditor.socket.QD_Socket`
"""
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

SOCKET_COLORS = [
    QColor("#FFFF7700"),
    QColor("#FF52e220"),
    QColor("#FF0056a6"),
    QColor("#FFa86db1"),
    QColor("#FFb54747"),
    QColor("#FFdbe220"),
    QColor("#FF888888"),
]


class QD_SocketGfx(QGraphicsItem):
    """Class representing Graphic `QD_Socket` in ``QGraphicsScene``
    """

    def __init__(self, socket: 'QD_Socket'):
        """
        :param socket: reference to :class:`~nodeeditor.socket.QD_Socket`
        :type socket: :class:`~nodeeditor.socket.QD_Socket`
        """
        super().__init__(socket.node.gfx)

        self.socket = socket

        self.isHighlighted = False

        self.radius = 6.0
        self.outline_width = 1.0
        self.initAssets()

    @property
    def socket_type(self):
        return self.socket.socket_type

    def getSocketColor(self, key):
        """Returns the ``QColor`` for this ``key``"""
        if type(key) == int:
            return SOCKET_COLORS[key]
        elif type(key) == str:
            return QColor(key)
        return Qt.transparent

    def changeSocketType(self):
        """Change the QD_Socket Type"""
        self._color_background = self.getSocketColor(self.socket_type)
        self._brush = QBrush(self._color_background)
        if confg.DEBUG:
            print("QD_Socket changed to:", self._color_background.getRgbF())

        self.update()

    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""

        # determine socket color
        self._color_background = self.getSocketColor(self.socket_type)
        self._color_outline = QColor("#FF000000")
        self._color_highlight = QColor("#FF37A6FF")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._pen_highlight = QPen(self._color_highlight)
        self._pen_highlight.setWidthF(2.0)
        self._brush = QBrush(self._color_background)

    def paint(self, painter, option:QStyleOptionGraphicsItem, widget=None):
        """Painting a circle"""
        painter.setBrush(self._brush)
        painter.setPen(self._pen if not self.isHighlighted else self._pen_highlight)
        painter.drawEllipse(QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius))


    def boundingRect(self) -> QRectF:
        """Defining Qt' bounding rectangle"""
        return QRectF(
            - self.radius - self.outline_width,
            - self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )
