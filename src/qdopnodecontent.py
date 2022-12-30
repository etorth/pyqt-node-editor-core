# -*- coding: utf-8 -*-
from qdserializable import QD_Serializable
from qdopnodecontentgfx import QD_OpNodeContentGfx


class QD_OpNodeContent(QD_Serializable):
    NodeContentGfx_class = QD_OpNodeContentGfx


    def __init__(self, node: 'QD_OpNode'):
        super().__init__()

        # node can be None which means this content is not bound to any node
        # used for adding sub-nodes in container nodes
        self.node = node
        self.initInnerClasses()


    def initInnerClasses(self):
        self.gfx = self.NodeContentGfx_class(self)


    def serialize(self) -> dict:
        return {'op_code': self.__class__.op_code} # added by @opNodeRegister


    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        return True
