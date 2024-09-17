from enum import Enum


class EventType(Enum):
    LOAD = "LOAD"
    UNLOAD = "UNLOAD"
    BUILD = "BUILD"
    RENAME = "RENAME"
    DELETE = "DELETE"
