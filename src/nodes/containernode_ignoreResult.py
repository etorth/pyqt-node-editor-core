from PyQt6.QtCore import *
from node import *
from qdutils import *


class ContainerNodeContent_ignoreResult(NodeContent):
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
class ContainerNode_ignoreResult(QD_Node):
    icon = "icons/editor.png"
    op_type = OPS_CONTAINER
    op_title = "忽略结果"

    def __init__(self, scene):
        super().__init__(scene, outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = ContainerNodeContent_ignoreResult(self)
        self.gfx = CalcGraphicsNode(self)

    def evalImplementation(self):
        u_value = 1 # hack
        s_value = int(u_value)
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.gfx.setToolTip("结果总是为True")

        self.evalChildren()

        return self.value
