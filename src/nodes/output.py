from PyQt6.QtCore import *
from calc_node_base import *
from qdutils import *


class CalcOutputContent(QDMNodeContentWidget):
    def initUI(self):
        self.lbl = QLabel("42", self)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)


@utils.register_opnode
class CalcNode_Output(CalcNode):
    icon = "icons/out.png"
    op_type = OPS_CHECKER
    op_code = OP_NODE_OUTPUT
    op_title = "Output"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])

    def initInnerClasses(self):
        self.content = CalcOutputContent(self)
        self.gfxNode = CalcGraphicsNode(self)

    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.gfxNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        val = input_node.eval()

        if val is None:
            self.gfxNode.setToolTip("Input is NaN")
            self.markInvalid()
            return

        self.content.lbl.setText("%d" % val)
        self.markInvalid(False)
        self.markDirty(False)
        self.gfxNode.setToolTip("")

        return val
