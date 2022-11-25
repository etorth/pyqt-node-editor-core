import sys
from PyQt6.QtCore import *

from qdutils import *
from qdmainwindow import QD_MainWindow

if __name__ == '__main__':
    QCoreApplication.setOrganizationName(confg.APP_ORG)
    QCoreApplication.setApplicationName(confg.APP_NAME)

    app = QApplication(sys.argv)
    app.setStyle(confg.APP_STYLE)

    utils.mainWindow = QD_MainWindow()
    utils.mainWindow.setWindowTitle(confg.APP_TITLE)
    utils.mainWindow.show()

    sys.exit(app.exec())
