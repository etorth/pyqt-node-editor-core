# -*- encoding: utf-8 -*-
"""Module with some helper functions and config variables
"""

class Confg:
    APP_NAME    = 'QuestDesigner'
    APP_AUTHOR  = 'etorth'
    APP_ORG     = 'USTC'
    APP_VERSION = '0.1'
    APP_STYLE   = 'Fusion'

    def __init__(self):
        pass

    @property
    def APP_TITLE(self):
        return self.APP_NAME + '-' + self.APP_VERSION


class Utils:
    def __init__(self):
        pass

    def now(self):
        return '12.34.56'


confg = Confg()
utils = Utils()
