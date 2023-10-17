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
            except ValueError as e:
                self.display_error(str(e))
                return False

        return True
