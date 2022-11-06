import sys

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from qdutils import *
from mainwindow import MainWindow

if __name__ == '__main__':
    QCoreApplication.setOrganizationName(confg.APP_ORG)
    QCoreApplication.setApplicationName(confg.APP_NAME)

    app = QApplication(sys.argv)
    app.setStyle(confg.APP_STYLE)

    win = MainWindow()
    win.setWindowTitle(confg.APP_TITLE)
    win.show()

    utils.debugObj(win)
    sys.exit(app.exec())
