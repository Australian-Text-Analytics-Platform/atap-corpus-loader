from pandas import DataFrame
from panel import Tabs

from corpusloader.controller import Controller
from corpusloader.view.gui import AbstractWidget, FileLoaderWidget, OniLoaderWidget


class ViewWrapperWidget(AbstractWidget):
    def __init__(self, controller: Controller, base_path: str):
        super().__init__()
        self.controller: Controller = controller

        self.file_loader: FileLoaderWidget = FileLoaderWidget(self, controller, base_path)
        self.oni_loader: OniLoaderWidget = OniLoaderWidget(controller)

        self.panel = Tabs(("File Loader", self.file_loader), ("Oni Loader", self.oni_loader))
        self.children = [self.file_loader, self.oni_loader]

    def update_display(self):
        pass

    def get_loaded_corpus_df(self) -> DataFrame:
        return self.controller.get_loaded_corpus_df()

    def load_corpus_from_filepaths(self, filepath_ls: list[str]) -> bool:
        success = self.controller.load_corpus_from_filepaths(filepath_ls)
        self.update_displays()
        return success

    def load_meta_from_filepaths(self, filepath_ls: list[str]) -> bool:
        success = self.controller.load_meta_from_filepaths(filepath_ls)
        self.update_displays()
        return success
