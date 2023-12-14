from enum import Enum


class DataType(Enum):
    STRING = 'string'
    INTEGER = 'Int64'
    FLOAT = 'Float64'
    BOOLEAN = 'boolean'
    DATETIME = 'datetime64[ns]'
    CATEGORY = 'category'
