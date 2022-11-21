from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from node import Node
from nodecontent import NodeContent
from nodegfx import NodeGfx
from qsocket import LEFT_CENTER, RIGHT_CENTER
from qdutils import *


class CalcGraphicsNode(NodeGfx):
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 74
        self.edge_roundness = 6
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10

    def initAssets(self):
        super().initAssets()
        self.icons = QImage("icons/status_icons.png")

    def paint(self, painter, option: QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, option, widget)

        offset = 24.0
        if self.node.isDirty(): offset = 0.0
        if self.node.isInvalid(): offset = 48.0

        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.0),
            self.icons,
            QRectF(offset, 0, 24.0, 24.0)
        )


class CalcNode(Node):
    icon = ""
    op_title = "Undefined"

    NodeGfx_class = CalcGraphicsNode
    NodeContent_class = NodeContent

    def __init__(self, scene, inputs=[2, 2], outputs=[1]):
        super().__init__(scene, self.__class__.op_title, inputs, outputs)

        self.value = None

        # it's really important to mark all nodes Dirty by default
        self.markDirty()

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def evalOperation(self, input1, input2):
        return 123

    def evalImplementation(self):
        i1 = self.getInput(0)
        i2 = self.getInput(1)

        if i1 is None or i2 is None:
            self.markInvalid()
            self.markDescendantsDirty()
            self.gfx.setToolTip("Connect all inputs")
            return None

        else:
            val = self.evalOperation(i1.eval(), i2.eval())
            self.value = val
            self.markDirty(False)
            self.markInvalid(False)
            self.gfx.setToolTip("")

            self.markDescendantsDirty()
            self.evalChildren()

            return val

    def eval(self):
        if not self.isDirty() and not self.isInvalid():
            print(" _> returning cached %s value:" % self.__class__.__name__, self.value)
            return self.value

        try:

            val = self.evalImplementation()
            return val
        except ValueError as e:
            self.markInvalid()
            self.gfx.setToolTip(str(e))
            self.markDescendantsDirty()
        except Exception as e:
            self.markInvalid()
            self.gfx.setToolTip(str(e))
            utils.dumpExcept(e)

    def onInputChanged(self, socket=None):
        print("%s::__onInputChanged" % self.__class__.__name__)
        self.markDirty()
        self.eval()

    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        print("Deserialized CalcNode '%s'" % self.__class__.__name__, "res:", res)
        return res
