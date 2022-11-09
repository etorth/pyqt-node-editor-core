from PyQt6.QtCore import *
from calc_node_base import *
from qdutils import *


class LogicNodeContent_and(QDMNodeContentWidget):
    def initUI(self):
        self.label = QLabel('Lua代码')

        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(10, 10, 10, 10)
        self.hbox.setSpacing(10)

        self.hbox.addWidget(self.label)

    def serialize(self):
        res = super().serialize()
        res['value'] = 'lua_code_from_LuaEditorWidget'
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
class LogicNode_and(CalcNode):
    icon = "icons/editor.png"
    op_type = OPS_LOGIC
    op_code = OP_NODE_LOGIC_AND
    op_title = "逻辑与"

    def __init__(self, scene):
        super().__init__(scene, outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = LogicNodeContent_and(self)
        self.gfxNode = CalcGraphicsNode(self)

    def evalImplementation(self):
        u_value = 1 # hack
        s_value = int(u_value)
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.gfxNode.setToolTip("")

        self.evalChildren()

        return self.value