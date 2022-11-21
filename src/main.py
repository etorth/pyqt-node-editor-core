import sys
from PyQt6.QtCore import *

from qdutils import *
from qdmainwindow import QD_MainWindow

if __name__ == '__main__':
    QCoreApplication.setOrganizationName(confg.APP_ORG)
    QCoreApplication.setApplicationName(confg.APP_NAME)

    app = QApplication(sys.argv)
    app.setStyle(confg.APP_STYLE)

    win = QD_MainWindow()
    win.setWindowTitle(confg.APP_TITLE)
    win.show()

    sys.exit(app.exec())
