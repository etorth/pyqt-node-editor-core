# -*- coding: utf-8 -*-
from collections import OrderedDict
from qdserializable import QD_Serializable
from nodecontentgfx import NodeContentGfx


class NodeContent(QD_Serializable):
    NodeContentGfx_class = NodeContentGfx


    def __init__(self, node: 'Node'):
        super().__init__()

        self.node = node
        self.initInnerClasses()


    def initInnerClasses(self):
        self.gfx = self.NodeContentGfx_class(self)


    def serialize(self) -> OrderedDict:
        return OrderedDict([])


    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        return True
