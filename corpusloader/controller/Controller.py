from pandas import DataFrame

from corpusloader.controller.CorpusService import CorpusService
from corpusloader.controller.document.FileLoadError import FileLoadError
from corpusloader.view.ViewWrapperWidget import ByteIO
from corpusloader.view.notifications import NotifierService


class Controller:
    def __init__(self, corpus_service: CorpusService, notifier_service: NotifierService):
        self.corpus_service: CorpusService = corpus_service
        self.notifier_service: NotifierService = notifier_service

    def display_error(self, error_msg: str):
        self.notifier_service.notify_error(error_msg)

    def display_success(self, success_msg: str):
        self.notifier_service.notify_success(success_msg)

    def get_file_loader_info(self) -> list[dict]:
        return CorpusService.get_file_loader_info()

    def get_loaded_corpus_df(self) -> DataFrame:
        return self.corpus_service.get_corpus().to_dataframe()

    def load_corpus_from_filepaths(self, filepath_ls: list[str], loader_strategy_name: str) -> bool:
        try:
            self.corpus_service.load_corpus_from_filepaths(filepath_ls, loader_strategy_name)
        except (FileLoadError, ValueError) as e:
            self.display_error(f"File load error: {str(e)}")
            return False
        except Exception as e:
            self.display_error(f"Unexpected error while loading: {e.__repr__()}")
            return False

        return True

    def load_corpus_from_bytes(self, filebytes_ls: list[ByteIO]) -> bool:
        pass
