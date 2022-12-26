# -*- encoding: utf-8 -*-
import bisect
import pprint
import traceback

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
    _node_type_uid = 0
    _node_type_list = {}

    _main_window = None
    _mono_font_families = None

    _node_state_icons = QImage("icons/status_icons.png")


    @property
    def main_window(self):
        return self._main_window


    @main_window.setter
    def main_window(self, win):
        if self._main_window is None:
            self._main_window = win
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
    def register_opnode(cls, node_type):
        cls._node_type_uid += 1
        node_type.op_code = cls._node_type_uid
        node_type.NodeContent_class.op_code = cls._node_type_uid
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


    def draw_node_state_icon(self, painter: QPainter, index: int, x: float, y: float, topleft: bool = True):
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
        match index % 7:
            case 0: return QColor('#800000')
            case 1: return QColor('#008000')
            case 2: return QColor('#808000')
            case 3: return QColor('#000080')
            case 4: return QColor('#800080')
            case 5: return QColor('#008080')
            case 6: return QColor('#005f87')
            case _: return QColor('#00875f')


utils = Utils()

from nodes import *
