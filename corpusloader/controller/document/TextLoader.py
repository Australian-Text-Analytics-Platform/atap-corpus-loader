import os

from corpusloader.controller.document.DocumentLoader import DocumentLoader
from corpusloader.controller.document.FileLoadError import FileLoadError
from corpusloader.model.corpus import Corpus


class TextLoader(DocumentLoader):
    def __init__(self):
        self.lines: list[str] = []
        self.content_name: str = ""
        self.loaded: bool = False

    def load_document_as_bytes(self, content: bytes, content_name: str):
        if self.loaded:
            raise FileLoadError(f"Document already loaded: {content_name}")

        content_str: str = content.decode('utf-8')
        self.lines = content_str.split('\n')
        self.content_name = content_name
        self.loaded = True

    def load_document_by_filepath(self, filepath: str):
        if self.loaded:
            raise FileLoadError(f"Document already loaded: {filepath}")

        with open(filepath) as f:
            file_str: str = f.read()
            self.lines = file_str.split()

        self.content_name = os.path.basename(filepath)
        self.loaded = True

    def add_to_corpus(self, corpus: Corpus):
        if not self.loaded:
            raise FileLoadError("No document loaded")

        content_name: list[str] = [self.content_name] * len(self.lines)

        corpus.add_data("lines", self.lines, False)
        corpus.add_data("text_id", content_name, True)
