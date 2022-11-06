# -*- encoding: utf-8 -*-
import pprint
import traceback

from PyQt6.QtCore import QFile
from PyQt6.QtWidgets import QApplication


OPS_NONE    = 0
OPS_COMMAND = 1
OPS_CHECKER = 2

UROLE_NONE = 0
UROLE_ICON = 1
UROLE_TYPE = 2


class Confg:
    APP_NAME    = 'QuestDesigner'
    APP_AUTHOR  = 'etorth'
    APP_ORG     = 'USTC'
    APP_VERSION = '0.1'
    APP_STYLE   = 'Fusion'


    DEBUG = True

    def __init__(self):
        pass

    @property
    def APP_TITLE(self):
        return self.APP_NAME + '-' + self.APP_VERSION


confg = Confg()


class Utils:
    def __init__(self):
        self._pprint = pprint.PrettyPrinter(indent=4)


    def printObj(self, obj):
        if confg.DEBUG:
            self._pprint.pprint(obj)


    def dumpExcept(self, e=None):
        traceback.print_exc()


    def loadStylesheet(self, filename: str):
        file = QFile(filename)
        file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        QApplication.instance().setStyleSheet(str(file.readAll(), encoding='utf-8'))


    def loadStylesheets(self, *args):
        sheets = []
        for arg in args:
            file = QFile(arg)
            file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
            sheets.append(str(file.readAll(), encoding='utf-8'))
        QApplication.instance().setStyleSheet('\n'.join(sheets))


utils = Utils()
