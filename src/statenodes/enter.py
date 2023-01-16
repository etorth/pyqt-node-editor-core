# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdstatewidget import QD_StateWidget
from qdsocket import *
from qdutils import *
from qdstatenode import QD_StateNode
from qdstatenodegfx import QD_StateNodeGfx

from qdutils import *
from qdwidgets import *


class _StateNodeWidget_enter(utils.disableAutoDelete(QWidget)):
    def __init__(self, node: 'StateNode_enter' = None, parent: QWidget = None):
        super().__init__(parent)

        self.node = node
        self.scene = self.node.scene
        self.initUI()


    def initUI(self):
        self.vbox = QVBoxLayout(self)
        if "CreateJobRequest":
            jobReqGroupBox = QGroupBox('可选择职业')
            jobReqGroupBox.setToolTip('该任务线角色可选择职业')

            self.warrior = QCheckBox('战士')
            self.wizard  = QCheckBox('法师')
            self.taoist  = QCheckBox('道士')

            self.warrior.setChecked(True)

            jobReqLayout = QVBoxLayout(jobReqGroupBox)
            jobReqLayout.addWidget(self.warrior)
            jobReqLayout.addWidget(self.wizard)
            jobReqLayout.addWidget(self.taoist)

            self.vbox.addWidget(jobReqGroupBox)

        if "CreateLevelRequest":
            levelReqGroupBox = QGroupBox('角色等级要求')
            levelReqGroupBox.setToolTip('该任务线角色等级要求')

            self.level = QD_RelationalConditionHBoxLayout('等级', levelReqGroupBox)
            self.vbox.addWidget(levelReqGroupBox)

        if "CreateGoldRequest":
            goldReqGroupBox = QGroupBox('角色金币要求')
            goldReqGroupBox.setToolTip('该任务线角色金币要求')

            self.gold = QD_RelationalConditionHBoxLayout('金币', goldReqGroupBox)
            self.vbox.addWidget(goldReqGroupBox)

        if 'CreateBlankArea':
            self.vbox.addWidget(QFrame())


class _StateNodeGfx_enter(QD_StateNodeGfx):
    StateNodeWidget_class = _StateNodeWidget_enter


    def __init__(self, node: 'QD_StateNode', parent: QGraphicsItem = None):
        super().__init__(node, parent)

        self.hovered = False
        self._was_moved = False
        self._last_selected_state = False

        self.initSizes()
        self.initAssets()
        self.initUI()


    @property
    def width(self) -> int:
        return self._rect_width


    @property
    def height(self) -> int:
        return self._rect_height


    def initUI(self):
        pass


    def initSizes(self):
        self._rect_width = 80
        self._rect_height = 60

        self._rect_text_width  = 50
        self._rect_text_height = 25


    def initAssets(self):
        self._color = QColor("#7F000000")
        self._colorText = QColor("#FF2F2835")
        self._colorTextBackground = QColor("#E3FFFFFF")

        self._colorHovered = QColor("#FF37A6FF")
        self._colorSelected = QColor("#FFF7862F")
        self._colorHoverSelected = QColor("#FFFFA637")

        self._pen = QPen(self._color)
        self._pen.setWidthF(2.0)
        self._pen_text = QPen(self._colorText)
        self._pen_text.setWidthF(2.0)
        self._pen_selected = QPen(self._colorSelected)
        self._pen_selected.setWidthF(2.0)
        self._pen_hovered = QPen(self._colorHovered)
        self._pen_hovered.setWidthF(3.0)
        self._pen_hover_selected = QPen(self._colorHoverSelected)
        self._pen_hover_selected.setWidthF(3.0)

        self._image = QImage("icons/src.png")

    def onSelected(self):
        self.node.scene.gfx.itemSelected.emit()

    def doSelect(self, new_state=True):
        self.setSelected(new_state)
        self._last_selected_state = new_state

        if new_state:
            self.onSelected()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        for node in self.scene().scene.nodes:
            if node.gfx.isSelected():
                node.updateConnectedEdges()
        self._was_moved = True

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.storeHistory("QD_OpNode moved", setModified=True)

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
        win = utils.mainWindow.findMdiChildByStateNode(self)
        if win:
            utils.mainWindow.mdiArea.setActiveSubWindow(win)
        else:
            subwin = utils.mainWindow.createMdiChild(self.node.widget)
            subwin.show()


    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = False
        self.update()

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height).normalized()


    def paint(self, painter, option: QStyleOptionGraphicsItem, widget=None):
        path_content = QPainterPath()
        path_content.setFillRule(Qt.FillRule.WindingFill)
        path_content.addEllipse(QRectF(0, 0, self.width, self.height))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.playerColor()))
        painter.drawPath(path_content.simplified())

        path_text = QPainterPath()
        path_text.setFillRule(Qt.FillRule.WindingFill)

        text_x = max(0, (self.width  - self._rect_text_width ) / 2)
        text_y = max(0, (self.height - self._rect_text_height) / 2)
        text_w = self.width  - 2 * text_x
        text_h = self.height - 2 * text_y

        path_text.addPolygon(QPolygonF([QPointF(text_x, text_y), QPointF(text_x + text_w, text_y), QPointF(self.width, self.height / 2), QPointF(text_x + text_w, text_y + text_h), QPointF(text_x, text_y + text_h)]))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._colorTextBackground))
        painter.drawPath(path_text.simplified())

        painter.setPen(self._pen_text)
        painter.drawText(QRectF(text_x, text_y, text_w, text_h), Qt.AlignmentFlag.AlignCenter, '玩家%d' % self.node.index)

        path_outline = QPainterPath()
        path_outline.addEllipse(QRectF(-1, -1, self.width + 2, self.height + 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self.hovered:
            painter.setPen(self._pen_hover_selected if self.isSelected() else self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_selected if self.isSelected() else self._pen)
            painter.drawPath(path_outline.simplified())

        if self.node.isDirty():
            utils.drawNodeStateIcon(painter, 1, self.width / 2, 0, False)
        elif self.node.isInvalid():
            utils.drawNodeStateIcon(painter, 2, self.width / 2, 0, False)
        else:
            utils.drawNodeStateIcon(painter, 0, self.width / 2, 0, False)


@utils.stateNodeRegister
class StateNode_enter(QD_StateNode):
    stateName = '进入'

    StateNodeWidget_class = _StateNodeWidget_enter
    StateNodeGfx_class = _StateNodeGfx_enter
    def __init__(self, scene: 'QD_QuestScene', sockets: set = {SocketType.Out_True}):
        super().__init__(scene, sockets)
        self.widget = _StateNodeWidget_enter(self)

        # TODO
        # get_next_valid_start_index() searches all StateNode_enter for existing index
        # but also searches to this obj under construction which has no index yet, bad design

        indics = {}
        for item in scene.gfx.items():
            if isinstance(item, utils.getStateNodeType('StateNode_enter').StateNodeGfx_class) and hasattr(item.node, 'index'):
                indics[item.node.index] = True

        i = 1
        while i in indics:
            i += 1

        self.index = i


    def getSocketPosition(self, socktype: SocketType) -> QPointF:
        assert socktype is SocketType.Out_True, socktype
        return QPointF(self.gfx.width, self.gfx.height / 2)


    def serialize(self) -> dict:
        return super().serialize() | {
            'index': self.index,
            'widget': {
                'job': {
                    'warrior': self.widget.warrior.isChecked(),
                    'wizard': self.widget.wizard.isChecked(),
                    'taoist': self.widget.taoist.isChecked(),
                },

                'level': {
                    'rationalIndex': self.widget.level.choice.currentIndex(),
                    'value': self.widget.level.edit.text(),
                },

                'gold': {
                    'rationalIndex': self.widget.level.choice.currentIndex(),
                    'value': self.widget.level.edit.text(),
                },
            },
        }


    def deserialize(self, data: dict, hashmap: dict = {}, restoreId: bool = True):
        super().deserialize(data, hashmap, restoreId)
        self.index = data['index']

        self.widget.warrior.setChecked(data['widget']['job']['warrior'])
        self.widget.wizard.setChecked(data['widget']['job']['wizard'])
        self.widget.taoist.setChecked(data['widget']['job']['taoist'])

        self.widget.level.choice.setCurrentIndex(data['widget']['level']['rationalIndex'])
        self.widget.level.edit.setText(data['widget']['level']['value'])

        self.widget.gold.choice.setCurrentIndex(data['widget']['gold']['rationalIndex'])
        self.widget.gold.edit.setText(data['widget']['gold']['value'])
