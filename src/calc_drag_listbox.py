from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from calc_conf import *
from utils import dumpException


class QDMDragListBox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._collapsed = False
        self.initUI()

    def initUI(self):
        # init
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)

        self.addMyItems()

        self.itemClicked.connect(self.onItemClicked)
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)

    def addMyItems(self):
        item = QListWidgetItem('父控件 ' + ('>' if self._collapsed else 'v'), self)
        item.setSizeHint(QSize(32, 32))
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

        if not self._collapsed:
            for key in sorted(list(CALC_NODES.keys())):
                node = get_class_from_opcode(key)
                self.addMyItem(node.op_title, node.icon, node.op_code)


    def addMyItem(self, name, icon=None, op_code=0):
        item = QListWidgetItem(name, self)  # can be (icon, text, parent, <int>type)
        pixmap = QPixmap(icon if icon is not None else ".")
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))

        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.ItemDataRole.UserRole, pixmap)
        item.setData(Qt.ItemDataRole.UserRole + 1, op_code)

    def startDrag(self, *args, **kwargs):
        try:
            item = self.currentItem()
            op_code = item.data(Qt.ItemDataRole.UserRole + 1)

            pixmap = QPixmap(item.data(Qt.ItemDataRole.UserRole))

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
            dumpException(e)


    def onItemClicked(self, item):
        print("Clicked: ", item.text())


    def onItemDoubleClicked(self, item):
        self.clear()
        self._collapsed = not self._collapsed
        self.addMyItems()