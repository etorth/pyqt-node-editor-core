import sys
from PyQt6.QtWidgets import *

from calc_window import CalculatorWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyle('Fusion')

    wnd = CalculatorWindow()
    wnd.show()

    sys.exit(app.exec())