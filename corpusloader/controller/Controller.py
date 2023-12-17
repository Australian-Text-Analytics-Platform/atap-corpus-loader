from typing import Optional

from atap_corpus.corpus.corpus import DataFrameCorpus
from pandas import DataFrame

from corpusloader.controller.FileLoaderService import FileLoaderService, FileLoadError
from corpusloader.controller.OniAPIService import OniAPIService
from corpusloader.controller.data_objects.CorpusHeader import CorpusHeader
from corpusloader.controller.data_objects.DataType import DataType
from corpusloader.view.notifications import NotifierService


class Controller:
    def __init__(self, notifier_service: NotifierService):
        self.file_loader_service: FileLoaderService = FileLoaderService()
        self.oni_api_service: OniAPIService = OniAPIService()
        self.notifier_service: NotifierService = notifier_service

        self.text_header: Optional[CorpusHeader] = None
        self.corpus_link_header: Optional[CorpusHeader] = None
        self.meta_link_header: Optional[CorpusHeader] = None

        self.corpus_headers: list[CorpusHeader] = []
        self.meta_headers: list[CorpusHeader] = []

        self.corpus: Optional[DataFrameCorpus] = None

    def display_error(self, error_msg: str):
        self.notifier_service.notify_error(error_msg)

    def display_success(self, success_msg: str):
        self.notifier_service.notify_success(success_msg)

    def get_loaded_corpus_df(self) -> Optional[DataFrame]:
        if self.corpus is None:
            return None
        return self.corpus.to_dataframe()

    def load_corpus_from_filepaths(self, filepath_ls: list[str]) -> bool:
        for filepath in filepath_ls:
            try:
                self.file_loader_service.add_corpus_filepath(filepath)
            except FileLoadError as e:
                self.display_error(str(e))
                return False

        self.corpus_headers = self.file_loader_service.get_inferred_corpus_headers()

        return True

    def load_meta_from_filepaths(self, filepath_ls: list[str]) -> bool:
        for filepath in filepath_ls:
            try:
                self.file_loader_service.add_meta_filepath(filepath)
            except FileLoadError as e:
                self.display_error(str(e))
                return False

        self.meta_headers = self.file_loader_service.get_inferred_meta_headers()

        return True

    def build_corpus(self, corpus_name: str):
        if self.is_meta_added():
            if (self.corpus_link_header is None) or (self.meta_link_header is None):
                self.display_error("Cannot build without link headers set. Select a corpus header and a meta header as linking headers in the dropdowns")
                return

        self.corpus = self.file_loader_service.build_corpus(corpus_name, self.corpus_headers,
                                                            self.meta_headers, self.text_header,
                                                            self.corpus_link_header, self.meta_link_header)

    def unload_all(self):
        self.file_loader_service.remove_all_files()

        self.text_header = None
        self.corpus_headers = []
        self.meta_headers = []

    def get_loaded_corpus_files(self) -> list[str]:
        return self.file_loader_service.get_loaded_corpus_files()

    def get_loaded_meta_files(self) -> list[str]:
        return self.file_loader_service.get_loaded_meta_files()

    def get_corpus_headers(self) -> list[CorpusHeader]:
        return self.corpus_headers

    def get_meta_headers(self) -> list[CorpusHeader]:
        return self.meta_headers

    def get_inferred_corpus_headers(self) -> list[CorpusHeader]:
        return self.file_loader_service.get_inferred_corpus_headers()

    def get_inferred_meta_headers(self) -> list[CorpusHeader]:
        return self.file_loader_service.get_inferred_meta_headers()

    def get_text_header(self) -> Optional[CorpusHeader]:
        return self.text_header

    def get_corpus_link_header(self) -> Optional[CorpusHeader]:
        return self.corpus_link_header

    def get_meta_link_header(self) -> Optional[CorpusHeader]:
        return self.meta_link_header

    def get_all_datatypes(self) -> list[str]:
        return [d.name for d in DataType]

    def is_corpus_added(self) -> bool:
        return len(self.corpus_headers) > 0

    def is_meta_added(self) -> bool:
        return len(self.meta_headers) > 0

    def update_corpus_header(self, header: CorpusHeader, include: Optional[bool], datatype_name: Optional[str]):
        if include is not None:
            header.include = include
        if datatype_name is not None:
            header.datatype = DataType[datatype_name]

        for i, corpus_header in enumerate(self.corpus_headers):
            if header == corpus_header:
                self.corpus_headers[i] = header

    def update_meta_header(self, header: CorpusHeader, include: Optional[bool], datatype_name: Optional[str]):
        if include is not None:
            header.include = include
        if datatype_name is not None:
            header.datatype = DataType[datatype_name]

        for i, meta_header in enumerate(self.meta_headers):
            if header == meta_header:
                self.meta_headers[i] = header

    def set_text_header(self, text_header: Optional[str]):
        if text_header is None:
            self.text_header = None
            return

        for header in self.corpus_headers:
            if header.name == text_header:
                self.text_header = header
                header.datatype = DataType['STRING']
                header.include = True
                return

    def set_corpus_link_header(self, link_header_name: Optional[str]):
        for header in self.corpus_headers:
            if header.name == link_header_name:
                self.corpus_link_header = header
                header.include = True
                return
        self.corpus_link_header = None

    def set_meta_link_header(self, link_header_name: Optional[str]):
        for header in self.meta_headers:
            if header.name == link_header_name:
                self.meta_link_header = header
                header.include = True
                return
        self.meta_link_header = None
