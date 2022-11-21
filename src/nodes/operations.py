from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdnode import *
from qdutils import *
from qdnodecontentgfx import *

class _CalcNodeBase(QD_Node):
    op_type = OPS_COMMAND


@utils.register_opnode
class _CalcNode_add(_CalcNodeBase):
    icon = "icons/add.png"
    op_title = "加"


    def evalOperation(self, input1, input2):
        return input1 + input2


@utils.register_opnode
class _CalcNode_sub(_CalcNodeBase):
    icon = "icons/sub.png"
    op_title = "减"


    def evalOperation(self, input1, input2):
        return input1 - input2


@utils.register_opnode
class _CalcNode_mul(_CalcNodeBase):
    icon = "icons/mul.png"
    op_title = "乘"


    def evalOperation(self, input1, input2):
        print('foo')
        return input1 * input2


@utils.register_opnode
class _CalcNode_div(_CalcNodeBase):
    icon = "icons/divide.png"
    op_title = "除"


    def evalOperation(self, input1, input2):
        return input1 / input2
