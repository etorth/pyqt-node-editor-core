# -*- coding: utf-8 -*-
"""A module containing Graphics representation of :class:`~nodeeditor.node.QD_Node`
"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class QD_NodeGfx(QGraphicsItem):
    """Class describing Graphics representation of :class:`~nodeeditor.node.QD_Node`"""

    def __init__(self, node: 'QD_Node', parent: QWidget = None):
        """
        :param node: reference to :class:`~nodeeditor.node.QD_Node`
        :type node: :class:`~nodeeditor.node.QD_Node`
        :param parent: parent widget
        :type parent: QWidget

        :Instance Attributes:

            - **node** - reference to :class:`~nodeeditor.node.QD_Node`
        """
        super().__init__(parent)
        self.node = node

        # init our flags
        self.hovered = False
        self._was_moved = False
        self._last_selected_state = False

        self.initSizes()
        self.initAssets()
        self.initUI()

    @property
    def content(self):
        """Reference to `QD_Node Content`"""
        return self.node.content if self.node else None

    @property
    def title(self):
        """title of this `QD_Node`

        :getter: current Graphics QD_Node title
        :setter: stores and make visible the new title
        :type: str
        """
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    @property
    def width(self) -> int:
        if self.content is not None:
            return max(self.content.gfx.width(), self._mini_width)
        else:
            return self._mini_width


    @property
    def height(self) -> int:
        if self.content is not None:
            return max(self.content.gfx.height(), self._mini_height)
        else:
            return self._mini_height


    def initUI(self):
        """Set up this ``QGraphicsItem``"""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setAcceptHoverEvents(True)

        # init title
        self.initTitle()
        self.title = self.node.title

        self.initContent()

    def initSizes(self):
        """Set up internal attributes like `width`, `height`, etc."""
        self._mini_width = 160
        self._mini_height = 74

        self.edge_roundness = 6
        self.edge_padding = 4
        self.title_height = 24
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10

    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._title_color = Qt.GlobalColor.white
        self._title_font = QFont("Ubuntu", 10)

        self._color = QColor("#7F000000")
        self._color_selected = QColor("#FFFFA637")
        self._color_hovered = QColor("#FF37A6FF")

        self._pen_default = QPen(self._color)
        self._pen_default.setWidthF(2.0)
        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(2.0)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_hovered.setWidthF(3.0)

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        self._icons = QImage("icons/status_icons.png")

    def onSelected(self):
        """Our event handling when the node was selected"""
        self.node.scene.gfx.itemSelected.emit()

    def doSelect(self, new_state=True):
        """Safe version of selecting the `Graphics QD_Node`. Takes care about the selection state flag used internally

        :param new_state: ``True`` to select, ``False`` to deselect
        :type new_state: ``bool``
        """
        self.setSelected(new_state)
        self._last_selected_state = new_state

        if new_state:
            self.onSelected()

    def mouseMoveEvent(self, event):
        """Overriden event to detect that we moved with this `QD_Node`"""
        super().mouseMoveEvent(event)

        # optimize me! just update the selected nodes
        for node in self.scene().scene.nodes:
            if node.gfx.isSelected():
                node.updateConnectedEdges()
        self._was_moved = True

    def mouseReleaseEvent(self, event):
        """Overriden event to handle when we moved, selected or deselected this `QD_Node`"""
        super().mouseReleaseEvent(event)

        # handle when gfx moved
        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.storeHistory("QD_Node moved", setModified=True)

            self.node.scene.resetLastSelectedStates()
            self.doSelect()  # also trigger itemSelected when node was moved

            # we need to store the last selected state, because moving does also select the nodes
            self.node.scene._last_selected_items = self.node.scene.getSelectedItems()

            # now we want to skip storing selection
            return

        # handle when gfx was clicked on
        if self._last_selected_state != self.isSelected() or self.node.scene._last_selected_items != self.node.scene.getSelectedItems():
            self.node.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def mouseDoubleClickEvent(self, event):
        """Overriden event for doubleclick. Resend to `QD_Node::onDoubleClicked`"""
        self.node.onDoubleClicked(event)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = False
        self.update()

    def boundingRect(self) -> QRectF:
        """Defining Qt' bounding rectangle"""
        return QRectF(0, 0, self.width, self.height).normalized()

    def initTitle(self):
        """Set up the title Graphics representation: font, color, position, etc."""
        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = self.node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.title_horizontal_padding, 0)
        self.title_item.setTextWidth(self.width - 2 * self.title_horizontal_padding)

    def initContent(self):
        """Set up the `proxy` - ``QGraphicsProxyWidget`` to have a container for `Graphics Content`"""
        if self.content.gfx is not None:
            self.content.gfx.setGeometry(round(self.edge_padding),
                                     round(self.title_height + self.edge_padding),
                                     round(self.width - 2 * self.edge_padding),
                                     round(self.height - 2 * self.edge_padding - self.title_height))

        # get the QGraphicsProxyWidget when inserted into the gfx
        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.content.gfx)


    def paint(self, painter, option: QStyleOptionGraphicsItem, widget=None):
        """Painting the rounded rectanglar `QD_Node`"""
        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, self.edge_roundness, self.edge_roundness)
        path_title.addRect(0, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        path_title.addRect(self.width - self.edge_roundness, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.FillRule.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(0, self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(self.width - self.edge_roundness, self.title_height, self.edge_roundness, self.edge_roundness)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(-1, -1, self.width + 2, self.height + 2, self.edge_roundness, self.edge_roundness)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self.hovered:
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
            painter.drawPath(path_outline.simplified())

        offset = 24.0
        if self.node.isDirty(): offset = 0.0
        if self.node.isInvalid(): offset = 48.0

        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.0),
            self._icons,
            QRectF(offset, 0, 24.0, 24.0)
        )
