# -*- coding: utf-8 -*-
"""
A module containing Graphics representation of QD_Edge
"""
import math
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

EDGE_CP_ROUNDNESS = 100  #: Bezier controll point distance on the line


class QD_EdgeGfx(QGraphicsPathItem):
    """Base class for Graphics QD_Edge"""

    def __init__(self, edge: 'QD_Edge', parent: QWidget = None):
        """
        :param edge: reference to :class:`qdedge.QD_Edge`
        :type edge: :class:`qdedge.QD_Edge`
        :param parent: parent widget
        :type parent: ``QWidget``

        :Instance attributes:

            - **edge** - reference to :class:`qdedge.QD_Edge`
            - **posSource** - ``[x, y]`` source position in the `QD_StateScene`
            - **posDestination** - ``[x, y]`` destination position in the `QD_StateScene`
        """
        super().__init__(parent)

        self.edge = edge

        # init our flags
        self._last_selected_state = False
        self.hovered = False

        # init our variables
        self.posSource = [0, 0]
        self.posDestination = [200, 100]

        self.initAssets()
        self.initUI()

    def initUI(self):
        """Set up this ``QGraphicsPathItem``"""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)

    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._color = QColor("#001000")
        self._color_pulse = QColor("#009999")
        self._color_selected = QColor("#00ff00")
        self._color_hovered = QColor("#FF37A6FF")
        self._pen = QPen(self._color)
        self._pen_pulse = QPen(self._color_pulse)
        self._pen_selected = QPen(self._color_selected)
        self._pen_dragging = QPen(self._color)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_dragging.setStyle(Qt.PenStyle.DashLine)
        self._pen.setWidthF(3.0)
        self._pen_pulse.setWidthF(3.0)
        self._pen_selected.setWidthF(3.0)
        self._pen_dragging.setWidthF(3.0)
        self._pen_hovered.setWidthF(5.0)

    def changeColor(self, color):
        """Change color of the edge from string hex value '#00ff00'"""
        # print("^Called change color to:", color.red(), color.green(), color.blue(), "on edge:", self.edge)
        self._color = QColor(color) if type(color) == str else color
        self._pen = QPen(self._color)
        self._pen.setWidthF(3.0)

    def setColorFromSockets(self) -> bool:
        """Change color according to connected sockets. Returns True if color can be determined
        """
        if self.edge.start_socket.type is not self.edge.end_socket.type:
            return False

        self.changeColor(self.edge.start_socket.color)
        return True

    def onSelected(self):
        """Our event handling when the edge was selected"""
        self.edge.scene.gfx.itemSelected.emit()

    def doSelect(self, new_state: bool = True):
        """Safe version of selecting the `Graphics QD_OpNode`. Takes care about the selection state flag used internally

        :param new_state: ``True`` to select, ``False`` to deselect
        :type new_state: ``bool``
        """
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state: self.onSelected()

    def mouseReleaseEvent(self, event):
        """Overriden Qt's method to handle selecting and deselecting this `Graphics QD_Edge`"""
        super().mouseReleaseEvent(event)
        if self._last_selected_state != self.isSelected():
            self.edge.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = False
        self.update()

    def setSource(self, x: float, y: float):
        """ Set source point

        :param x: x position
        :type x: ``float``
        :param y: y position
        :type y: ``float``
        """
        self.posSource = [x, y]

    def setDestination(self, x: float, y: float):
        """ Set destination point

        :param x: x position
        :type x: ``float``
        :param y: y position
        :type y: ``float``
        """
        self.posDestination = [x, y]

    def boundingRect(self) -> QRectF:
        """Defining Qt' bounding rectangle"""
        return self.shape().boundingRect()

    def shape(self) -> QPainterPath:
        """Returns ``QPainterPath`` representation of this `QD_Edge`

        :return: path representation
        :rtype: ``QPainterPath``
        """
        return self.calcPath()

    def paint(self, painter, option: QStyleOptionGraphicsItem, widget=None):
        """Qt's overriden method to paint this Graphics QD_Edge. Path calculated in :func:`qdedgegfx.QD_EdgeGfx.calcPath` method"""
        self.setPath(self.calcPath())

        painter.setBrush(Qt.BrushStyle.NoBrush)

        if self.hovered and self.edge.end_socket is not None:
            painter.setPen(self._pen_hovered)
            painter.drawPath(self.path())

        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            if self.isSelected():
                painter.setPen(self._pen_selected)
            elif self.edge.start_socket.type.is_pulse:
                painter.setPen(self._pen_pulse)
            else:
                painter.setPen(self._pen)

        painter.drawPath(self.path())

    def intersectsWith(self, p1: QPointF, p2: QPointF) -> bool:
        """Does this Graphics QD_Edge intersect with line between point A and point B ?

        :param p1: point A
        :type p1: ``QPointF``
        :param p2: point B
        :type p2: ``QPointF``
        :return: ``True`` if this `Graphics QD_Edge` intersects
        :rtype: ``bool``
        """
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calcPath()
        return cutpath.intersects(path)

    def calcPath(self) -> QPainterPath:
        """Will handle drawing QPainterPath from Point A to B

        :returns: ``QPainterPath`` of the edge connecting `source` and `destination`
        :rtype: ``QPainterPath``
        """
        raise NotImplementedError("This method has to be overriden in a child class")


class GfxEdgeDirect(QD_EdgeGfx):
    """Direct line connection Graphics QD_Edge"""

    def calcPath(self) -> QPainterPath:
        """Calculate the Direct line connection

        :returns: ``QPainterPath`` of the direct line
        :rtype: ``QPainterPath``
        """
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])
        return path


class GfxEdgeBezier(QD_EdgeGfx):
    """Cubic line connection Graphics QD_Edge"""

    def calcPath(self) -> QPainterPath:
        """Calculate the cubic Bezier line connection with 2 control points

        :returns: ``QPainterPath`` of the cubic Bezier line
        :rtype: ``QPainterPath``
        """
        s = self.posSource
        d = self.posDestination
        dist = (d[0] - s[0]) * 0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if self.edge.start_socket is not None:
            ssin = self.edge.start_socket.is_input
            ssout = self.edge.start_socket.is_output

            if (s[0] > d[0] and ssout) or (s[0] < d[0] and ssin):
                cpx_d *= -1
                cpx_s *= -1

                cpy_d = ((s[1] - d[1]) / math.fabs((s[1] - d[1]) if (s[1] - d[1]) != 0 else 0.00001)) * EDGE_CP_ROUNDNESS
                cpy_s = ((d[1] - s[1]) / math.fabs((d[1] - s[1]) if (d[1] - s[1]) != 0 else 0.00001)) * EDGE_CP_ROUNDNESS

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.cubicTo(s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d, self.posDestination[0], self.posDestination[1])

        return path
