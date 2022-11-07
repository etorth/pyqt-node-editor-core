from PyQt6.QtCore import *
from calc_node_base import *


@utils.register_opnode
class CalcNode_Add(CalcNode):
    icon = "icons/add.png"
    op_type = OPS_COMMAND
    op_code = OP_NODE_ADD
    op_title = "Add"
    content_label = "+"
    content_label_objname = "calc_node_bg"

    def evalOperation(self, input1, input2):
        return input1 + input2


@utils.register_opnode
class CalcNode_Sub(CalcNode):
    icon = "icons/sub.png"
    op_type = OPS_COMMAND
    op_code = OP_NODE_SUB
    op_title = "Substract"
    content_label = "-"
    content_label_objname = "calc_node_bg"

    def evalOperation(self, input1, input2):
        return input1 - input2

@utils.register_opnode
class CalcNode_Mul(CalcNode):
    icon = "icons/mul.png"
    op_type = OPS_COMMAND
    op_code = OP_NODE_MUL
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
    op_code = OP_NODE_DIV
    op_title = "Divide"
    content_label = "/"
    content_label_objname = "calc_node_div"

    def evalOperation(self, input1, input2):
        return input1 / input2

# way how to register by function call
# utils.register_opnode_now(OP_NODE_ADD, CalcNode_Add)
