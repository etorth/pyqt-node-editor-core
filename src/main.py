import sys

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from mainwindow import MainWindow

if __name__ == '__main__':
    QCoreApplication.setOrganizationName('USTC')
    QCoreApplication.setApplicationName('QuestDesigner')

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
