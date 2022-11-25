import sys
from PyQt6.QtCore import *

from qdutils import *
from qdmainwindow import QD_MainWindow

global g_mainWindow

if __name__ == '__main__':
    QCoreApplication.setOrganizationName(confg.APP_ORG)
    QCoreApplication.setApplicationName(confg.APP_NAME)

    app = QApplication(sys.argv)
    app.setStyle(confg.APP_STYLE)

    g_mainWindow = QD_MainWindow()
    g_mainWindow.setWindowTitle(confg.APP_TITLE)
    g_mainWindow.show()

    sys.exit(app.exec())
