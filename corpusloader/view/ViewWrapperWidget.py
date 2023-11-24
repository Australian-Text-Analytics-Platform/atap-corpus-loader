import panel as pn
from pandas import DataFrame
from panel import Row, Column
from panel.widgets import Button

from corpusloader.controller import Controller

from corpusloader.view.gui import AbstractWidget
from corpusloader.view.gui.loader import CorpusInfoWidget, FileLoaderWidget, OniLoaderWidget

pn.extension(notifications=True)


class ByteIO:
    pass


class ViewWrapperWidget(AbstractWidget):
    def __init__(self, controller: Controller, base_path: str):
        super().__init__()
        self.controller: Controller = controller

        self.corpus_info: CorpusInfoWidget = CorpusInfoWidget(self)
        self.file_loader: FileLoaderWidget = FileLoaderWidget(self, base_path)
        self.oni_loader: OniLoaderWidget = OniLoaderWidget(self)
        self.oni_loader.set_visibility(False)

        self.file_loader_button = Button(name="File loader",
                                         button_type="primary", button_style="solid")
        self.file_loader_button.on_click(self.toggle_file_loader)
        self.oni_loader_button = Button(name="Oni Loader",
                                        button_type="primary", button_style="outline")
        self.oni_loader_button.on_click(self.toggle_oni_loader)

        self.component = Column(
            Row(
                Column(self.file_loader_button,
                       self.oni_loader_button),
                self.file_loader.get_component(),
                self.oni_loader.get_component()
            ),
            self.corpus_info.get_component()
        )
        self.children = [self.corpus_info, self.file_loader, self.oni_loader]

    def update_display(self):
        pass

    def get_file_loader_info(self) -> list[dict]:
        return self.controller.get_file_loader_info()

    def get_loaded_corpus_df(self) -> DataFrame:
        return self.controller.get_loaded_corpus_df()

    def clear_loaded_corpus(self):
        self.corpus_info.clear_loaded_corpus()
        self.update_displays()

    def load_corpus_from_filepaths(self, filepath_ls: list[str], loader_strategy_name: str) -> bool:
        success = self.controller.load_corpus_from_filepaths(filepath_ls, loader_strategy_name)
        self.update_displays()
        return success

    def load_corpus_from_bytes(self, filebytes_ls: list[ByteIO]) -> bool:
        success = self.controller.load_corpus_from_bytes(filebytes_ls)
        self.update_displays()
        return success

    def toggle_file_loader(self, *args):
        self.oni_loader_button.button_style = "outline"

        if self.file_loader.get_visibility():
            self.file_loader_button.button_style = "outline"
            self.file_loader.set_visibility(False)
        else:
            self.file_loader_button.button_style = "solid"
            self.file_loader.set_visibility(True)
        self.oni_loader.set_visibility(False)

    def toggle_oni_loader(self, *args):
        self.file_loader_button.button_style = "outline"

        if self.oni_loader.get_visibility():
            self.oni_loader_button.button_style = "outline"
            self.oni_loader.set_visibility(False)
        else:
            self.oni_loader_button.button_style = "solid"
            self.oni_loader.set_visibility(True)
        self.file_loader.set_visibility(False)
