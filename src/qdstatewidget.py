# -*- coding: utf-8 -*-
import os
import json
from collections import OrderedDict

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdutils import *
from qdscene import QD_Scene, InvalidFile
from qdnode import QD_Node
from qdedge import QD_Edge, EdgeType
from qdviewgfx import QD_ViewGfx
from qdstateconfg import QD_StateConfg
from qddraglistbox import QD_DragListBox


class QD_StateWidget(QSplitter):
    Scene_class = QD_Scene


    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.filename = None

        self.initUI()

    def initUI(self):
        self.confg = QD_StateConfg()
        self.addWidget(self.confg.gfx)

        self.scene = self.__class__.Scene_class()
        self.view = QD_ViewGfx(self.scene.gfx)
        self.addWidget(self.view)

        self.draglist = QD_DragListBox()
        self.addWidget(self.draglist)

        self.setSizes([200, 800, 200])


    def onAttrTimeoutEditingFinished(self):
        if self._attr_timeout_edit.text():
            if int(self._attr_timeout_edit.text()) < 0:
                self._attr_timeout_edit.setText("无限制")


    def isModified(self) -> bool:
        return self.scene.isModified()


    def isFilenameSet(self) -> bool:
        return self.filename is not None


    def getSelectedItems(self) -> list:
        return self.scene.getSelectedItems()

    def hasSelectedItems(self) -> bool:
        return self.getSelectedItems() != []


    def canUndo(self) -> bool:
        return self.scene.history.canUndo()


    def canRedo(self) -> bool:
        return self.scene.history.canRedo()


    def getUserFriendlyFilename(self) -> str:
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Graph"
        return name + ("*" if self.isModified() else "")


    def fileNew(self):
        self.scene.clear()
        self.filename = None
        self.scene.history.clear()
        self.scene.history.storeInitialHistoryStamp()


    def fileLoad(self, filename: str):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            with open(filename, "r", encoding='utf-8') as f:
                data = json.load(f)

                if data['version'] != confg.APP_VERSION:
                    QMessageBox.warning(self, "Incompatible json file version: %s" % data['version'], "Current version is %s" % confg.APP_VERSION)
                    return False

                self.confg.deserialize(data['confg'])
                self.scene.deserialize(data['scene'])

                self.scene.has_been_modified = False
                self.scene.history.clear()
                self.scene.history.storeInitialHistoryStamp()

                self.filename = filename
                return True

        except InvalidFile as e:
            QMessageBox.warning(self, "Error loading json file: %s" % filename, str(e))
            return False

        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid json file: %s" % filename, str(e))
            return False

        finally:
            QApplication.restoreOverrideCursor()


    def fileSave(self, filename: str = None):
        if filename is not None:
            self.filename = filename

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        with open(self.filename, "w", encoding='utf-8', newline='\n') as f:
            json.dump(self.serialize(), f, ensure_ascii=False, indent=4)
            print('saving to %s was successfull.' % self.filename)
            self.scene.has_been_modified = False

        QApplication.restoreOverrideCursor()
        return True


    def addNodes(self):
        node1 = QD_Node(self.scene, "My Awesome QD_Node 1", sockets={SocketType.In, SocketType.Out_True, SocketType.Out_False})
        node2 = QD_Node(self.scene, "My Awesome QD_Node 2", sockets={SocketType.In, SocketType.Out_True, SocketType.Out_False})
        node3 = QD_Node(self.scene, "My Awesome QD_Node 3", sockets={SocketType.In, SocketType.Out_True, SocketType.Out_False})
        node1.setPos(-350, -250)
        node2.setPos(-75, 0)
        node3.setPos(200, -200)

        edge1 = QD_Edge(self.scene, node1.getSocket(SocketType.Out_True), node2.getSocket(SocketType.In), edge_type=EdgeType.Bezier)
        edge2 = QD_Edge(self.scene, node2.getSocket(SocketType.Out_True), node3.getSocket(SocketType.In), edge_type=EdgeType.Bezier)
        edge3 = QD_Edge(self.scene, node1.getSocket(SocketType.Out_True), node3.getSocket(SocketType.In), edge_type=EdgeType.Bezier)

        self.scene.history.storeInitialHistoryStamp()


    def addCustomNode(self):
        from qdnodecontent import QD_NodeContent
        from qdserializable import QD_Serializable

        class NNodeContent(QLabel):  # , QD_Serializable):
            def __init__(self, node, parent=None):
                super().__init__("FooBar")
                self.node = node
                self.setParent(parent)

        class NNode(QD_Node):
            NodeContent_class = NNodeContent

        self.scene.setNodeClassSelector(lambda data: NNode)
        node = NNode(self.scene, "A Custom QD_Node 1", sockets={SocketType.In, SocketType.Out_True, SocketType.Out_False})

        print("node content:", node.content)


    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('version', confg.APP_VERSION),
            ('confg', self.confg.serialize()),
            ('scene', self.scene.serialize()),
        ])


    def addDebugContent(self):
        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.black)
        outlinePen.setWidth(2)

        rect = self.gfx.addRect(-100, -100, 80, 100, outlinePen, greenBrush)
        rect.setFlag(QGraphicsItem.ItemIsMovable)

        text = self.gfx.addText("This is my Awesome text!", QFont("Ubuntu"))
        text.setFlag(QGraphicsItem.ItemIsSelectable)
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setDefaultTextColor(QColor.fromRgbF(1.0, 1.0, 1.0))

        widget1 = QPushButton("Hello World")
        proxy1 = self.gfx.addWidget(widget1)
        proxy1.setFlag(QGraphicsItem.ItemIsMovable)
        proxy1.setPos(0, 30)

        widget2 = QTextEdit()
        proxy2 = self.gfx.addWidget(widget2)
        proxy2.setFlag(QGraphicsItem.ItemIsSelectable)
        proxy2.setPos(0, 60)

        line = self.gfx.addLine(-200, -200, 400, -100, outlinePen)
        line.setFlag(QGraphicsItem.ItemIsMovable)
        line.setFlag(QGraphicsItem.ItemIsSelectable)
