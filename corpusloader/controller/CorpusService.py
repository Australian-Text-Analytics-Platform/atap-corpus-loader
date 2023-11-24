import os
from pathlib import Path
from typing import Type, Optional

from corpusloader.controller.document.CSVLoader import CSVLoader
from corpusloader.controller.document.CorpusFileLoader import CorpusFileLoader
from corpusloader.controller.document.DocumentLoader import DocumentLoader
from corpusloader.controller.document.SimpleTextLoader import SimpleTextLoader
from atap_corpus.corpus.corpus import DataFrameCorpus

from corpusloader.view.ViewWrapperWidget import ByteIO


class CorpusService:
    FILE_LOADER_STRATEGIES: list[Type[DocumentLoader]] = [SimpleTextLoader, CSVLoader, CorpusFileLoader]

    @staticmethod
    def get_file_loader_info() -> list[dict]:
        loader_info = []
        for loader in CorpusService.FILE_LOADER_STRATEGIES:
            curr_loader_info = {"name": loader.get_user_friendly_name(), "description": loader.get_data_description()}
            loader_info.append(curr_loader_info)
        return loader_info

    def __init__(self):
        self.corpus: DataFrameCorpus = DataFrameCorpus()

    def get_corpus(self) -> DataFrameCorpus:
        return self.corpus

    def load_corpus_from_filepaths(self, path_str_ls: list[str], loader_strategy_name: str):
        if len(path_str_ls) == 0:
            raise ValueError("No files provided")

        for path_str in path_str_ls:
            if not os.path.exists(path_str):
                raise ValueError(f"No file found at: {path_str}")
            if not os.access(path_str, os.R_OK):
                raise ValueError(f"No permissions to read the file: {path_str}")

        filepaths: list[Path] = [Path(path_str) for path_str in path_str_ls]

        document_loader: Optional[Type[DocumentLoader]] = None
        for loader in CorpusService.FILE_LOADER_STRATEGIES:
            if loader_strategy_name == loader.get_user_friendly_name():
                document_loader = loader
                break
        if document_loader is None:
            raise ValueError(f"{loader_strategy_name} is not a valid loading strategy")
        added_corpus: DataFrameCorpus

        self.corpus = document_loader.load_corpus_from_filepath(filepaths)

    def load_corpus_from_bytes(self, filebytes_ls: list[ByteIO]):
        if len(filebytes_ls) == 0:
            raise ValueError("No files provided")
