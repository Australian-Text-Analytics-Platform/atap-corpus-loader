from abc import ABC, abstractmethod

from corpusloader.model.corpus import Corpus


class DocumentLoader(ABC):
    @abstractmethod
    def load_document_as_bytes(self, content: bytes, content_name: str):
        raise NotImplementedError()

    @abstractmethod
    def load_document_by_filepath(self, filepath: str):
        raise NotImplementedError()

    @abstractmethod
    def add_to_corpus(self, corpus: Corpus):
        raise NotImplementedError()
