# -*- coding: utf-8 -*-
import os
import json
from collections import OrderedDict

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdscene import QD_Scene, InvalidFile
from qdnode import QD_Node
from qdedge import QD_Edge, EdgeType
from qdviewgfx import QD_ViewGfx
from qdstateconfg import QD_StateConfg


class QD_StateWidget(QWidget):
    Scene_class = QD_Scene


    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.filename = None

        self.initUI()

    def initUI(self):
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)

        self.splitter.addWidget(self.createLeftPannel())
        self.splitter.addWidget(self.createMiddlePannel())


    def createLeftPannel(self):
        self.confg = QD_StateConfg(self)
        return self.confg.gfx


    def createMiddlePannel(self):
        self.scene = self.__class__.Scene_class()
        self.view = QD_ViewGfx(self.scene.gfx)

        return self.view


    def onAttrTimeoutEditingFinished(self):
        if self._attr_timeout_edit.text():
            if int(self._attr_timeout_edit.text()) < 0:
                self._attr_timeout_edit.setText("无限制")


    def isModified(self) -> bool:
        """Has the `QD_Scene` been modified?

        :return: ``True`` if the `QD_Scene` has been modified
        :rtype: ``bool``
        """
        return self.scene.isModified()

    def isFilenameSet(self) -> bool:
        """Do we have graph loaded from file or new one?

        :return: ``True`` if filename is set. ``False`` if its a graph not saved to a file
        :rtype: ''bool''
        """
        return self.filename is not None

    def getSelectedItems(self) -> list:
        """Shortcut returning `QD_Scene`'s currently selected items

        :return: list of ``QGraphicsItems``
        :rtype: list[QGraphicsItem]
        """
        return self.scene.getSelectedItems()

    def hasSelectedItems(self) -> bool:
        """Is there something selected in the :class:`nodeeditor.scene.QD_Scene`?

        :return: ``True`` if there is something selected in the `QD_Scene`
        :rtype: ``bool``
        """
        return self.getSelectedItems() != []

    def canUndo(self) -> bool:
        """Can Undo be performed right now?

        :return: ``True`` if we can undo
        :rtype: ``bool``
        """
        return self.scene.history.canUndo()

    def canRedo(self) -> bool:
        """Can Redo be performed right now?

        :return: ``True`` if we can redo
        :rtype: ``bool``
        """
        return self.scene.history.canRedo()

    def getUserFriendlyFilename(self) -> str:
        """Get user friendly filename. Used in window title

        :return: just a base name of the file or `'New Graph'`
        :rtype: ``str``
        """
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Graph"
        return name + ("*" if self.isModified() else "")

    def fileNew(self):
        """Empty the scene (create new file)"""
        self.scene.clear()
        self.filename = None
        self.scene.history.clear()
        self.scene.history.storeInitialHistoryStamp()

    def fileLoad(self, filename: str):
        """Load serialized graph from JSON file

        :param filename: file to load
        :type filename: ``str``
        """
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            self.scene.loadFromFile(filename)
            self.filename = filename
            self.scene.history.clear()
            self.scene.history.storeInitialHistoryStamp()
            return True
        except InvalidFile as e:
            print(e)
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Error loading %s" % os.path.basename(filename), str(e))
            return False
        finally:
            QApplication.restoreOverrideCursor()

    def fileSave(self, filename: str = None):
        """Save serialized graph to JSON file. When called with empty parameter, we won't store/remember the filename

        :param filename: file to store the graph
        :type filename: ``str``
        """
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
        """Testing method to create 3 `Nodes` with 3 `Edges` connecting them"""
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
        """Testing method to create a custom QD_Node with custom content"""
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
            ('scene', self.scene.serialize()),
            ('confg', self.confg.serialize()),
        ])


    def addDebugContent(self):
        """Testing method to put random QGraphicsItems and elements into QGraphicsScene"""
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
