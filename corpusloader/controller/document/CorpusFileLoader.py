from io import BytesIO
from pathlib import Path
from typing import Optional

from corpusloader.controller.document.DocumentLoader import DocumentLoader
from corpusloader.controller.document.FileLoadError import FileLoadError


class CorpusFileLoader(DocumentLoader):
    USER_FRIENDLY_NAME: str = "Corpus file"
    DATA_DESCRIPTION: str = "A single .corpus file"

    @staticmethod
    def get_user_friendly_name():
        return CorpusFileLoader.USER_FRIENDLY_NAME

    @staticmethod
    def get_data_description():
        return CorpusFileLoader.DATA_DESCRIPTION

    def __init__(self):
        self.serialised_content: Optional[BytesIO] = None
        self.loaded: bool = False

    def load_corpus_from_bytes(self, content: bytes, content_name: str):
        if self.loaded:
            raise FileLoadError(f"Documents already loaded")
        self.serialised_content = content
        self.loaded = True

    def load_corpus_from_filepath(self, filepath: Path):
        if self.loaded:
            raise FileLoadError(f"Documents already loaded")



        self.loaded = True

    def generate_corpus(self):
        if not self.loaded:
            raise FileLoadError("No documents loaded")
