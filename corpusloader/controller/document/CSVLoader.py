from typing import Iterable

from corpusloader.controller.document.DocumentLoader import DocumentLoader
from corpusloader.controller.document.FileLoadError import FileLoadError
from corpusloader.model.corpus import Corpus


class CSVLoader(DocumentLoader):
    def __init__(self):
        self.content: list[str] = []
        self.content_header: str = ""
        self.meta_data: dict[str, Iterable] = {}
        self.loaded: bool = False

    def load_document_as_bytes(self, content: bytes, content_name: str):
        if self.loaded:
            raise FileLoadError(f"Document already loaded: {content_name}")
        self.loaded = True

    def load_document_by_filepath(self, filepath: str):
        if self.loaded:
            raise FileLoadError(f"Document already loaded: {filepath}")
        self.loaded = True

    def add_to_corpus(self, corpus: Corpus):
        if not self.loaded:
            raise FileLoadError("No document loaded")

        line_numbers: list[int] = list(range(1, len(self.content) + 1))

        corpus.add_data(self.content_header, self.content, False)
        corpus.add_data("line", line_numbers, True)
        for meta_name, meta_data in self.meta_data.items():
            corpus.add_data(meta_name, meta_data, True)
