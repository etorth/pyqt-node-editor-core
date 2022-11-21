from PyQt6.QtCore import *
from qdnode import *


@utils.register_opnode
class CalcNode_Add(QD_Node):
    icon = "icons/add.png"
    op_type = OPS_COMMAND
    op_title = "Add"

    def evalOperation(self, input1, input2):
        return input1 + input2


@utils.register_opnode
class CalcNode_Sub(QD_Node):
    icon = "icons/sub.png"
    op_type = OPS_COMMAND
    op_title = "Substract"

    def evalOperation(self, input1, input2):
        return input1 - input2

@utils.register_opnode
class CalcNode_Mul(QD_Node):
    icon = "icons/mul.png"
    op_type = OPS_COMMAND
    op_title = "Multiply"

    def evalOperation(self, input1, input2):
        print('foo')
        return input1 * input2

@utils.register_opnode
class CalcNode_Div(QD_Node):
    icon = "icons/divide.png"
    op_type = OPS_COMMAND
    op_title = "Divide"

    def evalOperation(self, input1, input2):
        return input1 / input2
