from fnmatch import fnmatch
from typing import Callable

import panel
from panel import Row, Column
from panel.widgets import Button, MultiSelect, TextInput, Select, Checkbox

from atap_corpus_loader.controller import Controller
from atap_corpus_loader.controller.data_objects import FileReference
from atap_corpus_loader.view.gui import AbstractWidget


class FileSelectorWidget(AbstractWidget):
    def __init__(self, view_handler: AbstractWidget, controller: Controller):
        super().__init__()
        self.view_handler: AbstractWidget = view_handler
        self.controller: Controller = controller
        # The function will be set by an instance method, but must be callable until then
        self._set_button_status_on_operation: Callable = lambda curr_loading: None

        self.select_all_button = Button(name="Select all", width=95,
                                        button_style="solid", button_type="primary")
        self.select_all_button.on_click(self.select_all)

        self.filter_input = TextInput(placeholder="Filter displayed files (supports wildcard syntax)",
                                      sizing_mode='stretch_width')
        self.filter_input.param.watch(self._on_filter_change, ['value'])

        self.show_hidden_files_checkbox = Checkbox(name="Show hidden", value=False, align="start")
        self.show_hidden_files_checkbox.param.watch(self._on_filter_change, ['value'])

        self.expand_archive_checkbox = Checkbox(name="Expand archives", value=False, align="start")
        self.expand_archive_checkbox.param.watch(self._on_filter_change, ['value'])

        self.file_type_filter = Select(width=150)
        self.file_type_filter.options = ['All valid filetypes'] + self.controller.get_valid_filetypes()
        self.file_type_filter.param.watch(self._on_filter_change, ['value'])

        self.selector_widget = MultiSelect(size=20, sizing_mode='stretch_width')

        self.panel = Column(
            Row(self.select_all_button),
            Row(self.filter_input,
                Column(
                    self.show_hidden_files_checkbox,
                    self.expand_archive_checkbox
                ),
                self.file_type_filter),
            Row(self.selector_widget),
            width=700)

        panel.state.add_periodic_callback(self.update_display, period=2000)
        self.update_display()

    def set_button_operation_fn(self, _set_button_status_on_operation: Callable):
        self._set_button_status_on_operation = _set_button_status_on_operation

    def update_display(self):
        loaded_corpus_files: set[FileReference] = self.controller.get_loaded_corpus_files()
        loaded_meta_files: set[FileReference] = self.controller.get_loaded_meta_files()

        filtered_refs: list[FileReference] = self._get_filtered_file_refs()

        filtered_files_dict: dict[str, str] = {}
        checkmark_symbol = "\U00002714"
        for ref in filtered_refs:
            file_repr = ref.get_path()
            if ref in loaded_corpus_files:
                file_repr += f" {checkmark_symbol} [corpus]"
            if ref in loaded_meta_files:
                file_repr += f" {checkmark_symbol} [meta]"
            filtered_files_dict[file_repr] = ref.get_path()

        self.selector_widget.options = filtered_files_dict

    def _get_filtered_file_refs(self) -> list[FileReference]:
        valid_file_types: list[str] = self.controller.get_valid_filetypes()
        selected_file_types: set[str]
        if self.file_type_filter.value in valid_file_types:
            selected_file_types = {self.file_type_filter.value.upper()}
        else:
            selected_file_types = {ft.upper() for ft in valid_file_types}

        expand_archived: bool = self.expand_archive_checkbox.value
        file_refs: list[FileReference] = self.controller.retrieve_all_files(expand_archived)

        filtered_refs: list[FileReference] = []
        filter_str = f"*{self.filter_input.value}*"
        skip_hidden: bool = not self.show_hidden_files_checkbox.value
        for ref in file_refs:
            if ref.get_extension().upper() not in selected_file_types:
                continue
            if not fnmatch(ref.get_path(), filter_str):
                continue
            if skip_hidden and ref.is_hidden():
                continue

            filtered_refs.append(ref)

        return filtered_refs

    def _on_filter_change(self, *_):
        self._set_button_status_on_operation(curr_loading=True)
        self.update_display()
        self._set_button_status_on_operation(curr_loading=False)

    def select_all(self, *_):
        self._set_button_status_on_operation(curr_loading=True)
        self.selector_widget.value = list(self.selector_widget.options.values())
        self._set_button_status_on_operation(curr_loading=False)

    def get_selector_value(self) -> list[str]:
        return self.selector_widget.value

    def get_show_hidden_value(self) -> bool:
        return self.show_hidden_files_checkbox.value
