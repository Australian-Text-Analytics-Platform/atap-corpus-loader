from enum import Enum


class DataType(Enum):
    """
    Maps readable data type names to the pandas data types
    """
    TEXT = 'string'
    INTEGER = 'int64'
    DECIMAL = 'float64'
    BOOLEAN = 'bool'
    DATETIME = 'datetime64[ns]'
    CATEGORY = 'category'
