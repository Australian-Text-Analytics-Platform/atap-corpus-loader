from fnmatch import fnmatch

import panel
from panel import Row, Column
from panel.widgets import Button, MultiSelect, TextInput, Select

from corpusloader.controller import Controller
from corpusloader.controller.data_objects import FileReference
from corpusloader.view.gui import AbstractWidget


class FileSelectorWidget(AbstractWidget):
    def __init__(self, view_handler: AbstractWidget, controller: Controller):
        super().__init__()
        self.view_handler: AbstractWidget = view_handler
        self.controller: Controller = controller

        self.select_all_button = Button(name="Select all", width=95,
                                        button_style="solid", button_type="primary")
        self.select_all_button.on_click(self.select_all)

        self.filter_input = TextInput(placeholder="Filter displayed files (supports wildcard syntax)",
                                      sizing_mode='stretch_width')
        self.filter_input.param.watch(self._on_filter_change, ['value_input'])

        self.file_type_filter = Select(width=150)
        self.file_type_filter.options = ['All valid filetypes'] + self.controller.get_valid_filetypes()
        self.file_type_filter.param.watch(self._on_filter_change, ['value'])

        self.selector_widget = MultiSelect(size=20, sizing_mode='stretch_width')

        self.panel = Column(
            Row(self.select_all_button),
            Row(self.filter_input,
                self.file_type_filter),
            Row(self.selector_widget),
            width=700)

        panel.state.add_periodic_callback(self.update_display, period=2000)
        self.update_display()
        self.select_all()

    def update_display(self):
        all_file_refs: list[FileReference] = self.controller.retrieve_all_files()
        loaded_corpus_files: list[FileReference] = self.controller.get_loaded_corpus_files()
        loaded_meta_files: list[FileReference] = self.controller.get_loaded_meta_files()

        valid_file_types: list[str] = self.controller.get_valid_filetypes()
        selected_file_types: list[str]
        if self.file_type_filter.value in valid_file_types:
            selected_file_types = [self.file_type_filter.value.upper()]
        else:
            selected_file_types = [ft.upper() for ft in valid_file_types]

        filter_str = f"*{self.filter_input.value_input}*"
        filtered_refs: list[FileReference] = []
        for ref in all_file_refs:
            extension: str = ref.get_extension().upper()
            if fnmatch(ref.get_relative_path(), filter_str) and (extension in selected_file_types):
                filtered_refs.append(ref)

        old_selected_refs: list[FileReference] = self.selector_widget.value.copy()
        filtered_selected_refs: list[FileReference] = [f for f in old_selected_refs if f in filtered_refs]

        filtered_files_dict: dict[str, FileReference] = {}
        checkmark_symbol = "\U00002714"
        for ref in filtered_refs:
            file_repr = ref.get_relative_path()
            if ref in loaded_corpus_files:
                file_repr += f" {checkmark_symbol} [corpus]"
            if ref in loaded_meta_files:
                file_repr += f" {checkmark_symbol} [meta]"
            filtered_files_dict[file_repr] = ref

        self.selector_widget.options = filtered_files_dict
        self.selector_widget.value = filtered_selected_refs

    def _on_filter_change(self, *_):
        self.update_display()
        self.select_all()

    def select_all(self, *_):
        self.selector_widget.value = list(self.selector_widget.options.values())

    def get_selector_value(self) -> list[FileReference]:
        return self.selector_widget.value
