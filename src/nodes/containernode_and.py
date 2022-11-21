from PyQt6.QtCore import *
from calc_node_base import *
from qdutils import *


class ContainerNodeContent_and(NodeContent):
    def initUI(self):
        self.label = QLabel('Lua代码')
        self.view = QGraphicsView()

        self.scene = QGraphicsScene()
        self.scene.addRect(0, 0, 100, 100)
        self.scene.addEllipse(0, 0, 100, 100)
        self.scene.addWidget(QLabel('Lua代码2'))

        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(10, 10, 10, 10)
        self.vbox.setSpacing(10)

        self.vbox.addWidget(self.label)

        self.view.setScene(self.scene)
        self.vbox.addWidget(self.view)

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
class ContainerNode_and(CalcNode):
    icon = "icons/editor.png"
    op_type = OPS_CONTAINER
    op_title = "逻辑与"

    def __init__(self, scene):
        super().__init__(scene, outputs=[3])
        self.eval()

    def addSubNode(self, node):
        newNode = node(self.scene)
        self.content.vbox.addWidget(QLabel('widget'))

    def initInnerClasses(self):
        self.content = ContainerNodeContent_and(self)
        self.gfx = CalcGraphicsNode(self)

    def evalImplementation(self):
        u_value = 1 # hack
        s_value = int(u_value)
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.gfx.setToolTip("")

        self.evalChildren()

        return self.value
