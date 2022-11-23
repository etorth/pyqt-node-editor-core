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


    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.content.node is not None:
            self.content.node.updateConnectedEdges()
            self.content.node.updateSockets()


class _ContainerContent_and(QD_NodeContent):
    NodeContentGfx_class =_ContainerContentGfx_and


    def __init__(self, node: 'QD_Node'):
        super().__init__(node)
        self._nested_contents = []


    def addSubNode(self, contentType):
        content = contentType(None)
        self._nested_contents.append(content)
        self.gfx.vbox.addWidget(content.gfx)
        return content


    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('nested_contents', [c.serialize() for c in self._nested_contents]),
        ])


    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        for content_data in data['nested_contents']:
            self.addSubNode(utils.get_class_from_opcode(content_data['op_code']).NodeContent_class).deserialize(content_data, hashmap, restore_id)
        return True


@utils.register_opnode
class _Container_and(QD_Node):
    icon = "icons/editor.png"
    op_type = OPS_CONTAINER
    op_title = "与"

    NodeContent_class = _ContainerContent_and


    def __init__(self, scene):
        super().__init__(scene)
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
        self.gfx.update()
        self.gfx.prepareGeometryChange()
        self.content.addSubNode(nodeType.NodeContent_class)
