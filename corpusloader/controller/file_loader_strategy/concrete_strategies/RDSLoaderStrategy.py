from pandas import DataFrame

from corpusloader.controller.data_objects import CorpusHeader
from corpusloader.controller.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class RDSLoaderStrategy(FileLoaderStrategy):
    def get_inferred_headers(self) -> list[CorpusHeader]:
        pass

    def get_dataframe(self, headers: list[CorpusHeader]) -> DataFrame:
        pass
