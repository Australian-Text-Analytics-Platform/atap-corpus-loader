from pandas import DataFrame

from corpusloader.controller.CorpusService import CorpusService
from corpusloader.controller.document.FileLoadError import FileLoadError
from corpusloader.view.notifications import NotifierService


class Controller:
    def __init__(self, corpus_service: CorpusService, notifier_service: NotifierService):
        self.corpus_service: CorpusService = corpus_service
        self.notifier_service: NotifierService = notifier_service

        self.corpus_headers = []
        self.corpus_datatypes = []
        self.meta_headers = []
        self.meta_datatypes = []

        self.all_datatypes = ['string', 'integer', 'float', 'datetime', 'category']

    def display_error(self, error_msg: str):
        self.notifier_service.notify_error(error_msg)

    def display_success(self, success_msg: str):
        self.notifier_service.notify_success(success_msg)

    def get_loaded_corpus_df(self) -> DataFrame:
        return self.corpus_service.build_corpus().to_dataframe()

    def load_corpus_from_filepaths(self, filepath_ls: list[str]) -> bool:
        # try:
        #     self.corpus_service.load_corpus_from_filepaths(filepath_ls)
        # except (FileLoadError, ValueError) as e:
        #     self.display_error(f"File load error: {str(e)}")
        #     return False
        # except Exception as e:
        #     self.display_error(f"Unexpected error while loading: {e.__repr__()}")
        #     return False

        # Dummy data for now
        self.corpus_headers = ['document', 'filename', 'directory']
        self.corpus_datatypes = ['string', 'string', 'category']
        return True

    def load_meta_from_filepaths(self, filebytes_ls: list[str]) -> bool:
        # Dummy data for now
        self.meta_headers = ['date', 'author', 'file_id', 'source']
        self.meta_datatypes = ['datetime', 'string', 'string', 'string']
        return True

    def unload_all(self):
        self.corpus_headers = []
        self.corpus_datatypes = []
        self.meta_headers = []
        self.meta_datatypes = []

    def get_corpus_headers(self) -> list[str]:
        return self.corpus_headers

    def get_corpus_datatypes(self) -> list[str]:
        return self.corpus_datatypes

    def get_meta_headers(self) -> list[str]:
        return self.meta_headers

    def get_meta_datatypes(self) -> list[str]:
        return self.meta_datatypes

    def get_all_datatypes(self) -> list[str]:
        return self.all_datatypes

    def is_corpus_added(self) -> bool:
        return len(self.get_corpus_headers()) > 0

    def is_meta_added(self) -> bool:
        return len(self.get_meta_headers()) > 0
