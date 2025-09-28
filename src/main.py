# -*- coding: utf-8 -*-
import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from qdutils import *
from qdmainwindow import QD_MainWindow

if __name__ == '__main__':
    QCoreApplication.setOrganizationName(confg.APP_ORG)
    QCoreApplication.setApplicationName(confg.APP_NAME)

    app = QApplication(sys.argv)
    app.setStyle(confg.APP_STYLE)

    utils.mainWindow = QD_MainWindow()
    utils.mainWindow.setWindowIcon(QIcon(confg.APP_ICON))
    utils.mainWindow.setWindowTitle(confg.APP_TITLE)
    utils.mainWindow.show()

    sys.exit(app.exec())