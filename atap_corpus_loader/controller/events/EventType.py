from enum import Enum, auto


class EventType(Enum):
    LOAD = auto()
    UNLOAD = auto()
    BUILD = auto()
    RENAME = auto()
    DELETE = auto()
