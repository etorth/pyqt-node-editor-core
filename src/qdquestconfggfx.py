# -*- coding: utf-8 -*-
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from qdutils import *

class QD_QuestConfgGfx(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.description = None
        self.timeout = None

        self.initUI()


    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

        if "CreateQuestName":
            self.name = QLineEdit()
            self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)

            name_label = QLabel("任务名称")
            name_label.setToolTip('显示于用户任务界面的\"任务名称\"')

            self.layout.addWidget(name_label)
            self.layout.addWidget(self.name)

        if "CreateQuestDescription":
            self.description = QTextEdit()

            description_label = QLabel("任务描述")
            description_label.setToolTip('显示于用户任务界面的\"任务描述\"')

            self.layout.addWidget(description_label)
            self.layout.addWidget(self.description)

        if "CreateQuestComment":
            self.comment = QTextEdit()

            comment_label = QLabel("任务注释")
            comment_label.setToolTip('任务编辑器可选注释信息')

            self.layout.addWidget(comment_label)
            self.layout.addWidget(self.comment)

        if "CreateQuestAllocationMethods":
            char_alloc_group_box = QGroupBox("角色分配方式")
            char_alloc_group_box.setToolTip('选择角色分配方式')

            char_alloced_by_order = QRadioButton("按队伍顺序")
            char_alloced_random   = QRadioButton("随机")

            char_alloced_by_order.setChecked(True)

            char_alloc_layout = QVBoxLayout(char_alloc_group_box)
            char_alloc_layout.addWidget(char_alloced_by_order)
            char_alloc_layout.addWidget(char_alloced_random)

            self.layout.addWidget(char_alloc_group_box)

        if "CreateQuestTriggerMethods":
            trigger_group_box = QGroupBox("触发方式")
            trigger_group_box.setToolTip('选择任务触发方式')

            triggered_by_callback  = QRadioButton("被动触发")
            triggered_by_condition = QRadioButton("条件触发")

            triggered_by_callback.setChecked(True)

            trigger_layout = QVBoxLayout(trigger_group_box)
            trigger_layout.addWidget(triggered_by_callback)
            trigger_layout.addWidget(triggered_by_condition)

            self.layout.addWidget(trigger_group_box)

        if "CreateQuestPlayerLimits":
            player_limit_layout = QHBoxLayout()
            player_limit_layout.setSpacing(5)

            player_limit_layout.addWidget(QLabel("人数限制"))
            player_limit_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

            self._attr_player_limit_min = QComboBox()
            self._attr_player_limit_min.addItems(player_limit_list)
            self._attr_player_limit_min.currentIndexChanged.connect(self.onAttrPlayerMinLimitChanged)
            player_limit_layout.addWidget(self._attr_player_limit_min)

            player_limit_layout.addWidget(QLabel("至"))

            self._attr_player_limit_max = QComboBox()
            self._attr_player_limit_max.addItems(player_limit_list + ["无限制"])
            player_limit_layout.addWidget(self._attr_player_limit_max)

            player_limit_layout.addWidget(QLabel("人"))

            player_limit_layout.addWidget(QFrame(), 1)

            self.layout.addLayout(player_limit_layout)

        if "CreateQuestTimeoutWidgets":
            timeout_layout = QHBoxLayout()
            timeout_layout.setSpacing(5)

            self.timeout = QLineEdit()
            self.timeout.setValidator(QIntValidator())
            self.timeout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.timeout.editingFinished.connect(self.onAttrTimeoutEditingFinished)

            self._attr_timeout_units = QComboBox()
            self._attr_timeout_units.addItems(["秒", "分钟", "小时", "天", "周", "月", "年"])

            timeout_layout.addWidget(QLabel("任务限时"))
            timeout_layout.addWidget(self.timeout)
            timeout_layout.addWidget(self._attr_timeout_units)

            self.layout.addLayout(timeout_layout)


    def onAttrTimeoutEditingFinished(self):
        if self.timeout.text():
            if int(self.timeout.text()) <= 0:
                self.timeout.setText("无限制")


    def onAttrPlayerMinLimitChanged(self, index):
        if self._attr_player_limit_max.currentIndex() < index:
            self._attr_player_limit_max.setCurrentIndex(index)

        for i in range(0, self._attr_player_limit_max.count()):
            self._attr_player_limit_max.model().item(i).setEnabled(i >= index)
