from enum import Enum


class EventType(Enum):
    """
    Each EventType represents a kind of event that can be triggered by or via the CorpusLoader.
    The EventTypes are explained below:
    LOAD: one or more corpus or metadata files has been loaded
    UNLOAD: one or more corpus or metadata files has been unloaded
    BUILD: One corpus has been built. The corpus object will be parsed to the callback function as an argument
    RENAME: One corpus has been renamed. The corpus object will be parsed to the callback function as an argument
    DELETE: One corpus has been removed from the corpora
    UPDATE: The corpora has been modified through corpus addition, deletion, or renaming.
    """
    LOAD = "LOAD"
    UNLOAD = "UNLOAD"
    BUILD = "BUILD"
    RENAME = "RENAME"
    DELETE = "DELETE"
    UPDATE = "UPDATE"

    def __str__(self):
        return self.value
