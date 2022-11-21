from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdnode import *
from qdutils import *
from qdnodecontentgfx import *


class _ContainerContentGfx_and(QD_NodeContentGfx):
    def initUI(self):
        self.edit = QLineEdit(self)


class _ContainerContent_and(QD_NodeContent):
    NodeContentGfx_class =_ContainerContentGfx_and

    def serialize(self):
        res = super().serialize()
        res['value'] = self.gfx.edit.text()
        return res


    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.gfx.edit.setText(value)
            return True & res
        except Exception as e:
            utils.dumpExcept(e)
        return res


@utils.register_opnode
class _Container_and(QD_Node):
    icon = "icons/editor.png"
    op_type = OPS_CONTAINER
    op_title = "或"

    NodeContent_class = _ContainerContent_and


    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[3])
        self.eval()


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
