from abc import ABC, abstractmethod

from pandas import DataFrame

from corpusloader.controller.data_objects import CorpusHeader


class FileLoaderStrategy(ABC):
    def __init__(self, filepath: str):
        self.filepath: str = filepath

    @staticmethod
    def _apply_selected_headers(df: DataFrame, headers: list[CorpusHeader]) -> DataFrame:
        headers_exclude: list[str] = [h.name for h in headers if not h.include]
        pruned_df: DataFrame = df.drop(columns=headers_exclude)
        dtypes = {h.name: h.datatype.value for h in headers if h.include}

        return pruned_df.astype(dtype=dtypes)

    @abstractmethod
    def get_inferred_headers(self) -> list[CorpusHeader]:
        raise NotImplementedError()

    @abstractmethod
    def get_dataframe(self, headers: list[CorpusHeader]) -> DataFrame:
        raise NotImplementedError()
