from PyQt6.QtCore import *
from node import *
from qdutils import *


class CalcOutputContent(NodeContent):
    def initUI(self):
        self.label = QLabel("42", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft)


@utils.register_opnode
class CalcNode_Output(Node):
    icon = "icons/out.png"
    op_type = OPS_CHECKER
    op_title = "Output"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])

    def initInnerClasses(self):
        self.content = CalcOutputContent(self)
        self.gfx = CalcGraphicsNode(self)

    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.gfx.setToolTip("Input is not connected")
            self.markInvalid()
            return

        val = input_node.eval()

        if val is None:
            self.gfx.setToolTip("Input is NaN")
            self.markInvalid()
            return

        self.content.label.setText("%d" % val)
        self.markInvalid(False)
        self.markDirty(False)
        self.gfx.setToolTip("")

        return val
