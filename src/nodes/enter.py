from PyQt6.QtCore import *
from calc_node_base import *
from qdutils import *


class CalcEditorContent(QDMNodeContentWidget):
    def initUI(self):
        self.label = QLabel('Lua代码')


        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(10, 10, 10, 10)
        self.hbox.setSpacing(10)

        self.hbox.addWidget(self.label)

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
class StateNode_Enter(CalcNode):
    icon = "icons/editor.png"
    op_type = OPS_ACTION
    op_code = OP_NODE_EDITOR
    op_title = "进入节点"
    content_label_objname = "进入节点"

    def __init__(self, scene):
        super().__init__(scene, outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = CalcEditorContent(self)
        self.gfxNode = CalcGraphicsNode(self)

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
