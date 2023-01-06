# -*- coding: utf-8 -*-
from qdutils import *

class QD_Serializable():
    def __init__(self):
        self.id = id(self)

    def serialize(self) -> dict:
        return {'id': self.id}

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        """Deserialization method.

        Params:
            data: serialized data
            hashmap: dictionary containing references (by id == key) to existing objects
            restore_id: True if we are creating new Sockets. False is usefull when loading existing sockets which we can keep the existing object's id
        """
        try:
            if restore_id:
                self.id = data['id']

            hashmap[data['id']] = self
        except Exception as e:
            utils.dumpExcept(e)

        return True
