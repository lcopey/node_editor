class Serializable:
    def __init__(self):
        super(Serializable, self).__init__()
        self.id = id(self)

    def serialize(self):
        raise NotImplemented

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        raise NotImplemented
