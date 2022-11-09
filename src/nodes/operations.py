from PyQt6.QtCore import *
from calc_node_base import *


@utils.register_opnode
class CalcNode_Add(CalcNode):
    icon = "icons/add.png"
    op_type = OPS_COMMAND
    op_title = "Add"
    content_label = "+"
    content_label_objname = "calc_node_bg"

    def evalOperation(self, input1, input2):
        return input1 + input2


@utils.register_opnode
class CalcNode_Sub(CalcNode):
    icon = "icons/sub.png"
    op_type = OPS_COMMAND
    op_title = "Substract"
    content_label = "-"
    content_label_objname = "calc_node_bg"

    def evalOperation(self, input1, input2):
        return input1 - input2

@utils.register_opnode
class CalcNode_Mul(CalcNode):
    icon = "icons/mul.png"
    op_type = OPS_COMMAND
    op_title = "Multiply"
    content_label = "*"
    content_label_objname = "calc_node_mul"

    def evalOperation(self, input1, input2):
        print('foo')
        return input1 * input2

@utils.register_opnode
class CalcNode_Div(CalcNode):
    icon = "icons/divide.png"
    op_type = OPS_COMMAND
    op_title = "Divide"
    content_label = "/"
    content_label_objname = "calc_node_div"

    def evalOperation(self, input1, input2):
        return input1 / input2
