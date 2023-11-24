from panel import Row, Column
from panel.widgets import FileSelector, Button, RadioButtonGroup

from corpusloader.view import ViewWrapperWidget
from corpusloader.view.gui import AbstractWidget
from corpusloader.view.gui.styles import file_loader_style


class FileLoaderWidget(AbstractWidget):
    def __init__(self, view_handler: ViewWrapperWidget, base_path: str):
        super().__init__()
        self.view_handler: ViewWrapperWidget = view_handler

        self.file_selector: FileSelector = FileSelector(directory=base_path, refresh_period=2000)
        self.load_corpus_button: Button = Button(name="Load corpus",
                                                 button_style="solid",
                                                 button_type="success")
        self.load_corpus_button.on_click(self.load_corpus)

        loader_names = [info["name"] for info in self.view_handler.get_file_loader_info()]
        self.loader_radio: RadioButtonGroup = RadioButtonGroup(
            name="Data loader mode",
            options=loader_names,
            orientation="vertical",
            button_style="outline",
            button_type="primary"
        )

        self.component = Row(self.file_selector,
                             Column(self.load_corpus_button,
                                    self.loader_radio),
                             styles=file_loader_style)

    def update_display(self):
        pass

    def load_corpus(self, *args):
        filepath_ls: list[str] = self.file_selector.value
        loader_strategy: str = self.loader_radio.value

        self.view_handler.load_corpus_from_filepaths(filepath_ls, loader_strategy)
