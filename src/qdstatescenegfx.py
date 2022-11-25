# -*- coding: utf-8 -*-
"""
A module containing Graphic representation of :class:`scene.QD_StateScene`
"""
import math
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class QD_StateSceneGfx(QGraphicsScene):
    """Class representing Graphic of :class:`scene.QD_StateScene`"""
    #: pyqtSignal emitted when some item is selected in the `QD_StateScene`
    itemSelected = pyqtSignal()
    #: pyqtSignal emitted when items are deselected in the `QD_StateScene`
    itemsDeselected = pyqtSignal()

    def __init__(self, scene: 'QD_StateScene', parent: QWidget = None):
        """
        :param scene: reference to the :class:`scene.QD_StateScene`
        :type scene: :class:`scene.QD_StateScene`
        :param parent: parent widget
        :type parent: QWidget
        """
        super().__init__(parent)

        self.scene = scene

        # settings
        self.gridSize = 20
        self.gridSquares = 5

        self.initAssets()
        self.setBackgroundBrush(self._color_background)

    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._color_background = QColor("#393949")
        self._color_light = QColor("#2f2f2f")
        self._color_dark = QColor("#292929")

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

    # the drag events won't be allowed until dragMoveEvent is overriden
    def dragMoveEvent(self, event):
        """Overriden Qt's dragMoveEvent to enable Qt's Drag Events"""
        pass

    def setSceneSize(self, width: int, height: int):
        """Set `width` and `height` of the `Graphics QD_StateScene`"""
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter: QPainter, rect: QRect):
        """Draw background scene grid"""
        super().drawBackground(painter, rect)

        # here we create our grid
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.gridSize)
        first_top = top - (top % self.gridSize)

        # compute all lines to be drawn
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.gridSize):
            if (x % (self.gridSize * self.gridSquares) != 0):
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.gridSize):
            if (y % (self.gridSize * self.gridSquares) != 0):
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))

        # draw the lines
        painter.setPen(self._pen_light)
        if lines_light:
            painter.drawLines(*lines_light)

        painter.setPen(self._pen_dark)
        if lines_dark:
            painter.drawLines(*lines_dark)
