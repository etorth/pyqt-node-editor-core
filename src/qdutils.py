# -*- encoding: utf-8 -*-
import pprint

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


    def debugObj(self, obj):
        if confg.DEBUG:
            self._pprint.pprint(obj)


utils = Utils()
