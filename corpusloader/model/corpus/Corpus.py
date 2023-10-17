from typing import Iterable

from pandas import DataFrame


class Corpus:
    def __init__(self):
        self._data: DataFrame = DataFrame()
        self._data_columns: list[str] = []
        self._meta_data_columns: list[str] = []

    def add_data(self, column_name: str, column_data: Iterable, is_meta_data: bool):
        if is_meta_data and (column_name not in self._meta_data_columns):
            self._meta_data_columns.append(column_name)
            self._data[column_name] = column_data
        elif (not is_meta_data) and (column_name not in self._data_columns):
            self._data_columns.append(column_name)
            self._data[column_name] = column_data
        else:
            raise ValueError("column doesn't match size of DataFrame")

    def get_data_columns(self) -> list[str]:
        return self._data_columns.copy()

    def get_meta_data_columns(self) -> list[str]:
        return self._meta_data_columns.copy()

    def get_column(self, column_name: str) -> DataFrame:
        return self._data[column_name]

    def get_all(self) -> DataFrame:
        return self._data

    def get_all_data(self) -> DataFrame:
        return self._data[self._data_columns]

    def get_all_meta_data(self) -> DataFrame:
        return self._data[self._meta_data_columns]
