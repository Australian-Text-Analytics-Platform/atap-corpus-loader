from pandas import DataFrame as PandasDataFrame

from corpusloader.controller.document import FileLoadError
from corpusloader.model.corpus import CorpusService
from corpusloader.view.notifications import NotifierService


class Controller:
    def __init__(self, corpus_service: CorpusService, notifier_service: NotifierService):
        self.corpus_service: CorpusService = corpus_service
        self.notifier_service: NotifierService = notifier_service

    def display_error(self, error_msg: str):
        self.notifier_service.notify_error(error_msg)

    def display_success(self, success_msg: str):
        self.notifier_service.notify_success(success_msg)

    def load_files_from_paths(self, filepath_ls: list[str]) -> bool:
        for filepath in filepath_ls:
            try:
                self.corpus_service.load_file_by_filepath(filepath)
            except FileLoadError as e:
                self.display_error(str(e))
                return False
            except Exception as e:
                self.display_error(f"Unexpected error while loading: {e.__repr__()}")
                return False

        return True

    def get_loaded_corpus_as_dataframe(self) -> PandasDataFrame:
        return self.corpus_service.get_loaded_corpus_as_dataframe()
