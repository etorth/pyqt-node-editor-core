# -*- coding: utf-8 -*-
from qdserializable import QD_Serializable

class QD_Node(QD_Serializable):
    def __init__(self, scene: 'QD_Scene'):
        super().__init__()
        self.scene = scene
