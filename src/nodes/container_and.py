from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdnode import *
from qdutils import *
from qdnodecontentgfx import *


class _ContainerContentGfx_and(QD_NodeContentGfx):
    def initUI(self):
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)


class _ContainerContent_and(QD_NodeContent):
    NodeContentGfx_class =_ContainerContentGfx_and


@utils.register_opnode
class _Container_and(QD_Node):
    icon = "icons/editor.png"
    op_type = OPS_CONTAINER
    op_title = "与"

    NodeContent_class = _ContainerContent_and


    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[3])
        self.list = []
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


    def addSubNode(self, nodeType):
        self.gfx.prepareGeometryChange()
        content = nodeType.NodeContent_class(self)
        self.list.append(content)
        self.content.gfx.vbox.addWidget(content.gfx)
