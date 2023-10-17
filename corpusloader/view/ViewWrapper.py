import panel as pn
from pandas import DataFrame as PandasDataFrame
from panel import Row, Column

from corpusloader.controller import Controller
from corpusloader.view.gui.loader import FileInfoWidget, FileLoaderWidget
from corpusloader.view.gui.display import DisplayWidget

pn.extension(notifications=True)


class ViewWrapper:
    def __init__(self, controller: Controller):
        self.controller: Controller = controller

        self.file_info: FileInfoWidget = FileInfoWidget(self)
        self.file_loader: FileLoaderWidget = FileLoaderWidget(self)

        self.display_widget: DisplayWidget = DisplayWidget(self)

        self.component = Column(
            Row(
                self.file_info.get_component(),
                self.file_loader.get_component()
            ),
            Row(
                self.display_widget.get_component()
            )
        )

    def get_component(self):
        return self.component

    def update_displays(self):
        self.file_info.update_displays()
        self.file_loader.update_displays()
        self.display_widget.update_displays()

    def clear_loaded_files(self):
        self.file_info.clear_loaded_files()

    def add_loaded_files(self, filepath_ls: list[str]) -> bool:
        success = self.controller.load_files_from_paths(filepath_ls)

        if success:
            self.file_info.add_files(filepath_ls)
            self.file_info.update_displays()

        return success
