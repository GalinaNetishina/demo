from enum import Enum


class ZepEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
