# -*- coding: utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
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

        if "CreateQuestNameWidgets":
            self.name = QLineEdit()
            self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)

            name_label = QLabel("任务名称")
            name_label.setToolTip('显示于用户任务界面的\"任务名称\"')

            self.layout.addWidget(name_label)
            self.layout.addWidget(self.name)

        if "CreateQuestDescriptionWidgets":
            self.description = QTextEdit()

            description_label = QLabel("任务描述")
            description_label.setToolTip('显示于用户任务界面的\"任务描述\"')

            self.layout.addWidget(description_label)
            self.layout.addWidget(self.description)

        if "CreateQuestCommentWidgets":
            self.comment = QTextEdit()

            comment_label = QLabel("任务注释")
            comment_label.setToolTip('任务编辑器可选注释信息')

            self.layout.addWidget(comment_label)
            self.layout.addWidget(self.comment)

        if "CreateQuestTriggerMethodWidgets":
            trigger_group_box = QGroupBox("触发方式")
            trigger_group_box.setToolTip('选择任务触发方式')

            triggered_by_callback  = QRadioButton("被动触发")
            triggered_by_condition = QRadioButton("条件触发")

            triggered_by_callback.setChecked(True)

            trigger_layout = QVBoxLayout(trigger_group_box)
            trigger_layout.addWidget(triggered_by_callback)
            trigger_layout.addWidget(triggered_by_condition)

            self.layout.addWidget(trigger_group_box)


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
