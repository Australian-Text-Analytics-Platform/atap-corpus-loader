from panel import Row
from panel.widgets import FileSelector, Button

from corpusloader.view import ViewWrapper
from corpusloader.view.gui import AbstractWidget
from corpusloader.view.gui.styles import file_loader_style


class FileLoaderWidget(AbstractWidget):
    def __init__(self, view_handler: ViewWrapper, base_path: str):
        self.view_handler: ViewWrapper = view_handler

        self.file_selector: FileSelector = FileSelector(directory=base_path, refresh_period=2000)
        self.toggle_selector_button: Button = Button(name="Hide")
        self.load_files_button: Button = Button(name="Load file(s)")

        self.selector_displayed: bool = True

        self.toggle_selector_button.on_click(self.toggle_selector)
        self.load_files_button.on_click(self.load_files)

        self.component = Row(self.toggle_selector_button,
                             self.file_selector,
                             self.load_files_button,
                             styles=file_loader_style)

    def get_component(self):
        return self.component

    def update_displays(self):
        pass

    def set_visibility(self, is_visible: bool):
        self.component.visible = is_visible

    def toggle_visibility(self):
        self.component.visible = not self.component.visible

    def show_selector(self):
        self.toggle_selector_button.name = "Hide"
        self.load_files_button.visible = True
        self.file_selector.visible = True

        self.selector_displayed = True

    def hide_selector(self):
        self.toggle_selector_button.name = "Show"
        self.load_files_button.visible = False
        self.file_selector.visible = False
        self.file_selector.value = []

        self.selector_displayed = False

    def toggle_selector(self, *args):
        if self.selector_displayed:
            self.hide_selector()
        else:
            self.show_selector()

    def load_files(self, *args):
        filepath_ls: list[str] = self.file_selector.value

        success = self.view_handler.add_loaded_files(filepath_ls)

        if success:
            self.hide_selector()
