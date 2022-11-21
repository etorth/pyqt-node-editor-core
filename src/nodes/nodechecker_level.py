from PyQt6.QtCore import *
from calc_node_base import *
from qdutils import *


class CalcCheckerContent(NodeWidget):
    def initUI(self):
        self.label = QLabel('等级')

        self.choice = QComboBox()
        self.choice.addItems(["大于", "小于", "等于", "不等于", "不大于", "不小于"])

        self.edit = QLineEdit()
        self.edit.setValidator(QIntValidator())
        self.edit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(10, 10, 10, 10)
        self.hbox.setSpacing(5)

        self.hbox.addWidget(self.label)
        self.hbox.addWidget(self.choice)
        self.hbox.addWidget(self.edit)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & res
        except Exception as e:
            utils.dumpExcept(e)
        return res


@utils.register_opnode
class NodeChecker_level(CalcNode):
    icon = "icons/checker.png"
    op_type = OPS_CHECKER
    op_title = "等级"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = CalcCheckerContent(self)
        self.gfx = CalcGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        self.value = 12
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.gfx.setToolTip("")

        self.evalChildren()
        return self.value
