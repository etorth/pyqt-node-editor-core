from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdutils import *


class QDMDragListBox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._collapsed = {}
        self.initUI()

    def initUI(self):
        # init
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)

        self.addOpItems()

        self.itemClicked.connect(self.onItemClicked)
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)

    def addOpItems(self):
        for op_type, node_types in sorted(utils.valid_nodes().items()):
            collapsed = self._collapsed.get(op_type, False)

            item = QListWidgetItem(('父控件 %d ' % op_type) + ('>' if collapsed else 'v'), self)
            item.setSizeHint(QSize(32, 32))
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            item.setData(Qt.ItemDataRole.UserRole + UROLE_OPTYPE, op_type)

            if not collapsed:
                for node in node_types:
                    self.addOpItem(node.op_title, node.icon, node.op_code)


    def addOpItem(self, name, icon=None, op_code=0):
        item = QListWidgetItem(name, self)
        pixmap = QPixmap(icon if icon is not None else ".")
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))

        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.ItemDataRole.UserRole + UROLE_ICON, pixmap)
        item.setData(Qt.ItemDataRole.UserRole + UROLE_TYPE, utils.get_class_from_opcode(op_code))

    def startDrag(self, *args, **kwargs):
        try:
            item = self.currentItem()
            op_code = item.data(Qt.ItemDataRole.UserRole + UROLE_TYPE).op_code
            pixmap = QPixmap(item.data(Qt.ItemDataRole.UserRole + UROLE_ICON))

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.OpenModeFlag.WriteOnly)
            dataStream << pixmap
            dataStream.writeInt(op_code)
            dataStream.writeQString(item.text())

            mimeData = QMimeData()
            mimeData.setData(LISTBOX_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
            drag.setPixmap(pixmap)

            drag.exec(Qt.DropAction.MoveAction)

        except Exception as e:
            utils.dumpExcept(e)


    def onItemClicked(self, item):
        print("Clicked: ", item.text())


    def onItemDoubleClicked(self, item):
        optype = item.data(Qt.ItemDataRole.UserRole + UROLE_OPTYPE)
        if optype is None:
            return

        self.clear()
        self._collapsed[optype] = not self._collapsed.get(optype, False)
        self.addOpItems()
