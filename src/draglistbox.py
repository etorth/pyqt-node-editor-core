from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdutils import *


class DragListBox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._collapsed = {}
        self.initUI()

    def initUI(self):
        # init
        self.setIconSize(QSize(48, 48))
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)

        self.addOpItems()

        self.itemClicked.connect(self.onItemClicked)
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)

    def createCollapsibleIcon(self, filename, collapsed, gap=0):
        icon1 = 'icons/%s.png' % ('fold' if collapsed else 'unfold')
        icon2 = filename

        img1 = QPixmap(icon1)
        img2 = QPixmap(icon2)

        image = QImage(img1.width() + gap + img2.width(), max(img1.height(), img2.height()), QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(QColor(Qt.GlobalColor.transparent))

        combined = QPixmap.fromImage(image)
        paint = QPainter(combined)

        paint.drawPixmap(0, (image.height() - img1.height()) // 2, 16, 16, img1)
        paint.drawPixmap(img1.width() + gap, 0, img2)

        return combined

    def addOpItems(self):
        for op_type, node_types in sorted(utils.valid_nodes().items()):
            collapsed = self._collapsed.get(op_type, False)

            item = QListWidgetItem(utils.ops_type_str(op_type), self)
            item.setSizeHint(QSize(32, 32))
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            item.setData(Qt.ItemDataRole.UserRole + UROLE_OPTYPE, op_type)
            item.setIcon(QIcon(self.createCollapsibleIcon('icons/checker.png', collapsed, 10)))

            if not collapsed:
                for node in node_types:
                    self.addOpItem(node)


    def addOpItem(self, node):
        item = QListWidgetItem(node.op_title, self)
        pixmap = QPixmap(node.icon if node.icon is not None else ".")
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))

        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.ItemDataRole.UserRole + UROLE_ICON, pixmap)
        item.setData(Qt.ItemDataRole.UserRole + UROLE_TYPE, node)

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
