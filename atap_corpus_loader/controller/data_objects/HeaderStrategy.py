from enum import Enum


class HeaderStrategy(Enum):
    """
    Describes the ways in which headers will be read from files
    """
    INFER = 'infer'
    HEADERS = 'header'
    NO_HEADERS = 'no_header'
