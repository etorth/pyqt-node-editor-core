# -*- encoding: utf-8 -*-
import bisect
import pprint
import traceback
import functools

from PyQt6.QtCore import QFile, QRectF
from PyQt6.QtGui import QFontDatabase, QImage, QPainter, QColor
from PyQt6.QtWidgets import QApplication

LISTBOX_MIMETYPE = "application/x-item"

OPS_NONE      = 0
OPS_ACTION    = 1
OPS_COMMAND   = 2
OPS_CHECKER   = 3
OPS_CONTAINER = 4

UROLE_NONE   = 0
UROLE_ICON   = 1
UROLE_TYPE   = 2
UROLE_OPTYPE = 3


class Confg:
    APP_NAME    = 'QuestDesigner'
    APP_AUTHOR  = 'etorth'
    APP_ORG     = 'USTC'
    APP_VERSION = '0.1'
    APP_STYLE   = 'Fusion'
    APP_ICON    = 'icons/qd.png'

    DEBUG = True

    def __init__(self):
        pass

    @property
    def APP_TITLE(self):
        return self.APP_NAME + '-' + self.APP_VERSION


confg = Confg()


class Utils:
    _opNodeTypeList = {}
    _stateNodeTypeList = {}

    _mainWindow = None
    _mono_font_families = None

    _node_state_icons = QImage("icons/status_icons.png")

    _color_table = [
        QColor('#00FF00'),
        QColor('#FF0000'),
        QColor('#FFFF00'),
        QColor('#0000FF'),
        QColor('#FF00FF'),
        QColor('#00FFFF'),
        QColor('#005F87'),
        QColor('#00975F'),
        QColor('#FABED4'),
        QColor('#AAFFB3'),
        QColor('#BFEF45'),

        # from: https://zhuanlan.zhihu.com/p/508870810
        # QColor('#E6194B'),
        # QColor('#3CB44B'),
        # QColor('#FFE119'),
        # QColor('#4363D8'),
        # QColor('#F58231'),
        # QColor('#911EB4'),
        # QColor('#42D4F4'),
        # QColor('#F032E6'),
        # QColor('#BFEF45'),
        # QColor('#FABED4'),
        # QColor('#469990'),
        # QColor('#DCBEFF'),
        # QColor('#9A6324'),
        # QColor('#FFFAC8'),
        # QColor('#800000'),
        # QColor('#AAFFC3'),
        # QColor('#808000'),
        # QColor('#FFD8B1'),
        # QColor('#000075'),
        # QColor('#A9A9A9'),
        # QColor('#FFFFFF'),
        # QColor('#000000'),
    ]


    @property
    def mainWindow(self):
        return self._mainWindow


    @mainWindow.setter
    def mainWindow(self, win):
        if self._mainWindow is None:
            self._mainWindow = win
        else:
            raise RuntimeError('Main window has already been created')

    @property
    def mono_font(self):
        if self._mono_font_families is None:
            mono_font_path = 'fonts/YaHeiMonacoHybrid.ttf'
            loaded_font = QFontDatabase.addApplicationFont(mono_font_path)
            if loaded_font < 0:
                raise RuntimeError('Cannot load customized font: %s' % mono_font_path)
            self._mono_font_families = QFontDatabase.applicationFontFamilies(loaded_font)
        return self._mono_font_families[0]

    @classmethod
    def opNodeRegister(cls, node_type):
        node_type.op_code = functools.reduce(lambda count, sublist: count + len(sublist), cls._opNodeTypeList.values(), 0) + 1
        node_type.NodeContent_class.op_code = node_type.op_code
        bisect.insort(cls._opNodeTypeList.setdefault(node_type.op_type, []), node_type, key=lambda x: str(x))


    @classmethod
    def stateNodeRegister(cls, nodeType):
        nodeType.stateCode = len(cls._stateNodeTypeList) + 1
        cls._stateNodeTypeList[nodeType.stateCode] = nodeType


    def get_class_from_opcode(self, op_code):
        for type in self.getOpNodeTypes():
            if type.op_code == op_code:
                return type


    def getOpNodeTypes(self):
        return sorted(sum(self._opNodeTypeList.values(), []), key=lambda x: (x.op_type, x.op_code))


    def getStateNodeTypes(self):
        return self._stateNodeTypeList.values()


    def getStateNodeType(self, arg):
        if isinstance(arg, str):
            for nodeType in self.getStateNodeTypes():
                if nodeType.__name__ == arg:
                    return nodeType
            raise RuntimeError('Cannot find state node type: %s' % arg)
        elif isinstance(arg, int):
            if arg in self._stateNodeTypeList:
                return self._stateNodeTypeList[arg]
            else:
                raise RuntimeError('Cannot find state node type: %d' % arg)
        else:
            raise RuntimeError('Invalid argument type: %s' % type(arg))


    def valid_nodes(self, op_type=None):
        if op_type is None:
            return self._opNodeTypeList
        else:
            return self._opNodeTypeList.get(op_type, [])

    def __init__(self):
        self._pprint = pprint.PrettyPrinter(indent=4)


    def drawNodeStateIcon(self, painter: QPainter, index: int, x: float, y: float, topleft: bool = True):
        icon_size = 24.0
        if not topleft:
            x -= icon_size / 2.0
            y -= icon_size / 2.0

        match index % 3:
            case 0: offset = icon_size * 1
            case 1: offset = icon_size * 0
            case _: offset = icon_size * 2

        painter.drawImage(QRectF(x, y, icon_size, icon_size), self._node_state_icons, QRectF(offset, 0, icon_size, icon_size))


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


    def ops_type_str(self, op_type) -> str:
        if op_type == OPS_ACTION:
            return '行为'
        elif op_type == OPS_COMMAND:
            return '命令'
        elif op_type == OPS_CHECKER:
            return '条件'
        elif op_type == OPS_CONTAINER:
            return '容器'
        else:
            return '未知'


    def player_color(self, index) -> QColor:
        return self._color_table[index % len(self._color_table)]


utils = Utils()

from nodes import *
from statenodes import *
