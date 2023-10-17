from corpusloader.controller.document import DocumentLoader
from corpusloader.controller.document.FileLoadError import FileLoadError
from corpusloader.model.corpus import Corpus


class ZipLoader(DocumentLoader):
    def __init__(self):
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