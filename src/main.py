# -*- coding: utf-8 -*-
import sys
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from qdutils import *
from qdmainwindow import QD_MainWindow

if __name__ == '__main__':
    # QCoreApplication.setOrganizationName(confg.APP_ORG)
    # QCoreApplication.setApplicationName(confg.APP_NAME)

    app = QApplication(sys.argv)
    app.setStyle(confg.APP_STYLE)

    utils.main_window = QD_MainWindow()

    utils.main_window.setWindowIcon(QIcon(confg.APP_ICON))
    utils.main_window.setWindowTitle(confg.APP_TITLE)
    utils.main_window.show()

    sys.exit(app.exec())
