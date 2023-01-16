# -*- coding: utf-8 -*-


class QD_SerdesPod():
    def __init__(self):
        self.id = id(self)


    def serialize(self) -> dict:
        return {'id': self.id}


    def deserialize(self, data: dict, hashmap: dict = {}, restoreId: bool = True):
        """Deserialization method.

        Params:
            data: serialized data
            hashmap: dictionary containing references (by id == key) to existing objects
            restoreId: True if we are creating new Sockets. False is usefull when loading existing sockets which we can keep the existing object's id
        """

        if restoreId:
            self.id = data['id']

        hashmap[data['id']] = self
