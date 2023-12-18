from abc import ABC, abstractmethod

from pandas import DataFrame

from corpusloader.controller.data_objects import CorpusHeader


class FileLoaderStrategy(ABC):
    def __init__(self, filepath: str):
        self.filepath: str = filepath

    @staticmethod
    def _apply_selected_dtypes(df: DataFrame, headers: list[CorpusHeader]) -> DataFrame:
        dtypes = {h.name: h.datatype.value for h in headers if h.include}

        return df.astype(dtype=dtypes)

    @abstractmethod
    def get_inferred_headers(self) -> list[CorpusHeader]:
        raise NotImplementedError()

    @abstractmethod
    def get_dataframe(self, headers: list[CorpusHeader]) -> DataFrame:
        raise NotImplementedError()
