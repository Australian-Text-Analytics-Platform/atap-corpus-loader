from enum import Enum


class EventType(Enum):
    LOAD = "LOAD"
    UNLOAD = "UNLOAD"
    BUILD = "BUILD"
    IMPORT = "IMPORT"
    RENAME = "RENAME"
    DELETE = "DELETE"
