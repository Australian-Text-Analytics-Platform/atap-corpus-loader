from panel import Column
from panel.pane import Markdown

from corpusloader.view import ViewWrapper
from corpusloader.view.gui import AbstractWidget
from corpusloader.view.gui.styles import file_info_style


class FileInfoWidget(AbstractWidget):
    def __init__(self, view_handler: ViewWrapper):
        self.view_handler: ViewWrapper = view_handler

        self.loaded_files: list[str] = []
        self.file_info_display: Markdown = Markdown(self.get_file_info_markdown())

        self.component = Column(self.file_info_display, styles=file_info_style)

    def get_component(self):
        return self.component

    def update_displays(self):
        self.file_info_display.object = self.get_file_info_markdown()

    def set_visibility(self, is_visible: bool):
        self.component.visible = is_visible

    def toggle_visibility(self):
        self.component.visible = not self.component.visible

    def clear_loaded_files(self):
        self.loaded_files = []

    def add_files(self, file_ls: list[str]):
        self.loaded_files.extend(file_ls)

    def get_loaded_files(self) -> list[str]:
        return self.loaded_files.copy()

    def get_file_info_markdown(self) -> str:
        num_files: int = len(self.loaded_files)
        file_str: str = '\n'.join(self.loaded_files)
        markdown_str: str = f"""
        **Files:** {num_files}
        
        ## Loaded Files
        
        {file_str}
        """

        return markdown_str
