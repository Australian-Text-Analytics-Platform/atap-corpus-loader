from abc import ABC, abstractmethod

from pandas import DataFrame

from corpusloader.controller.data_objects import CorpusHeader, FileReference


class FileLoaderStrategy(ABC):
    def __init__(self, file_ref: FileReference):
        self.file_ref: FileReference = file_ref

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
