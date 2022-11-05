from PyQt6.QtCore import *
from calc_conf import *
from calc_node_base import *
from utils import dumpException


class CalcCheckerContent(QDMNodeContentWidget):
    def initUI(self):
        self.label = QLabel('等级')

        self.choice = QComboBox(self)
        self.choice.addItems(["大于", "小于", "等于", "不等于", "不大于", "不小于"])

        self.edit = QLineEdit("1", self)
        self.edit.setValidator(QIntValidator())
        self.edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.edit.setObjectName(self.node.content_label_objname)

        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(10, 10, 10, 10)
        self.hbox.setSpacing(10)

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
            dumpException(e)
        return res


@register_node(OP_NODE_CHECKER)
class CalcNode_Checker(CalcNode):
    icon = "icons/checker.png"
    op_code = OP_NODE_CHECKER
    op_title = "Checker"
    content_label_objname = "calc_node_checker"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = CalcCheckerContent(self)
        self.gfxNode = CalcGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        u_value = self.content.edit.text()
        s_value = int(u_value)
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.gfxNode.setToolTip("")

        self.evalChildren()

        return self.value
