# -*- coding: utf-8 -*-
from collections import OrderedDict
from qdserializable import QD_Serializable
from qdnodecontentgfx import QD_NodeContentGfx


class QD_NodeContent(QD_Serializable):
    NodeContentGfx_class = QD_NodeContentGfx


    def __init__(self, node: 'QD_Node'):
        super().__init__()

        # node can be None which means this content is not bound to any node
        # used for adding sub-nodes in container nodes
        self.node = node
        self.initInnerClasses()


    def initInnerClasses(self):
        self.gfx = self.NodeContentGfx_class(self)


    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('op_code', self.__class__.op_code), # added by @register_opnode
        ])


    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        return True
