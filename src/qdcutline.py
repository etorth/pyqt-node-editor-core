# -*- coding: utf-8 -*-
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *


class QD_CutLine(QGraphicsItem):
    """Class representing Cutting Line used for cutting multiple `Edges` with one stroke"""

    def __init__(self, parent: QWidget = None):
        """
        :param parent: parent widget
        :type parent: ``QWidget``
        """
        super().__init__(parent)

        self.line_points = []

        self._pen = QPen(Qt.GlobalColor.white)
        self._pen.setWidthF(2.0)
        self._pen.setDashPattern([3, 3])

        self.setZValue(2)

    def boundingRect(self) -> QRectF:
        """Defining Qt' bounding rectangle"""
        return self.shape().boundingRect()

    def shape(self) -> QPainterPath:
        """Calculate the QPainterPath object from list of line points

        :return: shape function returning ``QPainterPath`` representation of Cutting Line
        :rtype: ``QPainterPath``
        """
        poly = QPolygonF(self.line_points)

        if len(self.line_points) > 1:
            path = QPainterPath(self.line_points[0])
            for pt in self.line_points[1:]:
                path.lineTo(pt)
        else:
            path = QPainterPath(QPointF(0, 0))
            path.lineTo(QPointF(1, 1))

        return path

    def paint(self, painter, option: QStyleOptionGraphicsItem, widget=None):
        """Paint the Cutting Line"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.line_points)
        painter.drawPolyline(poly)
