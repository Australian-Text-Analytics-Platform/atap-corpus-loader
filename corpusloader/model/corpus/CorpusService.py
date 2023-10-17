import os
from typing import Type

from pandas import DataFrame as PandasDataFrame

from corpusloader.controller.document.CSVLoader import CSVLoader
from corpusloader.controller.document.CorpusFileLoader import CorpusFileLoader
from corpusloader.controller.document.DocumentLoader import DocumentLoader
from corpusloader.controller.document.TextLoader import TextLoader
from corpusloader.controller.document.ZipLoader import ZipLoader
from corpusloader.model.corpus import Corpus


class CorpusService:
    FILE_TYPE_MAP: dict[str, Type[DocumentLoader]] = {
        "txt": TextLoader,
        "csv": CSVLoader,
        "zip": ZipLoader,
        "corpus": CorpusFileLoader
    }

    def __init__(self):
        self.corpus: Corpus = Corpus()

    def get_corpus(self) -> Corpus:
        return self.corpus

    def load_file_by_filepath(self, filepath: str):
        if not os.path.exists(filepath):
            raise ValueError(f"No database file found at: {filepath}")
        if not os.access(filepath, os.R_OK):
            raise ValueError(f"No permissions to read the file: {filepath}")

        basename: str = os.path.basename(filepath)
        filetype: str
        if len(basename.split('.')) == 1:
            filetype = "txt"
        else:
            filetype = basename.split('.')[-1]

        if filetype not in CorpusService.FILE_TYPE_MAP.keys():
            raise ValueError(f"File type not supported: {filetype}")

        document_loader: DocumentLoader = CorpusService.FILE_TYPE_MAP[filetype]()
        document_loader.load_document_by_filepath(filepath)
        document_loader.add_to_corpus(self.corpus)

    def get_loaded_corpus_as_dataframe(self) -> PandasDataFrame:
        return self.corpus.get_all()
