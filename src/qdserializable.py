# -*- coding: utf-8 -*-

class QD_Serializable():
    def __init__(self):
        self.id = id(self)

    def serialize(self) -> dict:
        raise NotImplementedError()

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        """Deserialization method.

        Params:
            data: serialized data
            hashmap: dictionary containing references (by id == key) to existing objects
            restore_id: True if we are creating new Sockets. False is usefull when loading existing sockets which we can keep the existing object's id
        """
        raise NotImplementedError()
