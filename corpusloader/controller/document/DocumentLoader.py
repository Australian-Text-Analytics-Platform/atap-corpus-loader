from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path

from atap_corpus.corpus.corpus import DataFrameCorpus


class DocumentLoader(ABC):
    @staticmethod
    @abstractmethod
    def get_user_friendly_name():
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_data_description():
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def load_corpus_from_bytes(content_ls: list[BytesIO], content_names: list[str]) -> DataFrameCorpus:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def load_corpus_from_filepath(filepath_ls: list[Path]) -> DataFrameCorpus:
        raise NotImplementedError()
