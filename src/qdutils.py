# -*- encoding: utf-8 -*-
import bisect
import pprint
import traceback

from PyQt6.QtCore import QFile
from PyQt6.QtWidgets import QApplication

LISTBOX_MIMETYPE = "application/x-item"

OP_NODE_INPUT = 1
OP_NODE_OUTPUT = 2
OP_NODE_ADD = 3
OP_NODE_SUB = 4
OP_NODE_MUL = 5
OP_NODE_DIV = 6
OP_NODE_CHECKER = 7
OP_NODE_EDITOR = 8


OPS_NONE    = 0
OPS_COMMAND = 1
OPS_CHECKER = 2

UROLE_NONE = 0
UROLE_ICON = 1
UROLE_TYPE = 2
UROLE_OPTYPE = 3


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
    _node_type_list = {}

    @classmethod
    def register_opnode(cls, node_type):
        bisect.insort(cls._node_type_list.setdefault(node_type.op_type, []), node_type, key=lambda x: str(x))


    def get_class_from_opcode(self, op_code):
        for type in self.valid_node_types():
            if type.op_code == op_code:
                return type


    def valid_node_types(self):
        return sorted(sum(self._node_type_list.values(), []), key=lambda x: (x.op_type, x.op_code))

    def valid_nodes(self, op_type=None):
        if op_type is None:
            return self._node_type_list
        else:
            return self._node_type_list.get(op_type, [])

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

from nodes import *
