from panel import Tabs, Column, Row

from corpusloader.controller import Controller
from corpusloader.controller.data_objects import FileReference
from corpusloader.view.gui import AbstractWidget, FileLoaderWidget, OniLoaderWidget, CorpusInfoWidget


class ViewWrapperWidget(AbstractWidget):
    def __init__(self, controller: Controller):
        super().__init__()
        self.controller: Controller = controller

        self.file_loader: AbstractWidget = FileLoaderWidget(self, controller)
        self.oni_loader: AbstractWidget = OniLoaderWidget(controller)
        self.corpus_display: AbstractWidget = CorpusInfoWidget(controller)

        self.panel = Column(
            Row(Tabs(("File Loader", self.file_loader), ("Oni Loader", self.oni_loader))),
            Row(self.corpus_display))
        self.children = [self.file_loader, self.oni_loader, self.corpus_display]

    def update_display(self):
        pass

    def load_corpus_from_filepaths(self, filepath_ls: list[FileReference]) -> bool:
        success = self.controller.load_corpus_from_filepaths(filepath_ls)
        self.update_displays()
        return success

    def load_meta_from_filepaths(self, filepath_ls: list[FileReference]) -> bool:
        success = self.controller.load_meta_from_filepaths(filepath_ls)
        self.update_displays()
        return success
