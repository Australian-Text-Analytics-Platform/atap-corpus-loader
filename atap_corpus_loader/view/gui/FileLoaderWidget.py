from panel import Row, Spacer, Column, HSpacer
from panel.pane import Markdown
from panel.widgets import Button, TextInput, TooltipIcon, Select

from atap_corpus_loader.controller import Controller
from atap_corpus_loader.view import ViewWrapperWidget
from atap_corpus_loader.view.gui import AbstractWidget
from atap_corpus_loader.view.gui.FileSelectorWidget import FileSelectorWidget
from atap_corpus_loader.view.gui.MetaEditorWidget import MetaEditorWidget


class FileLoaderWidget(AbstractWidget):
    LOADER_WIDTH: int = 600

    def __init__(self, view_handler: ViewWrapperWidget, controller: Controller, include_meta_loader: bool):
        super().__init__()
        self.view_handler: ViewWrapperWidget = view_handler
        self.controller: Controller = controller

        self.load_as_corpus_button: Button = Button(name='Load as corpus', width=130, button_style='outline',
                                                    button_type='success')
        self.load_as_corpus_button.on_click(self.load_as_corpus)
        if include_meta_loader:
            load_buttons_tooltip = self.view_handler.get_tooltip('load_buttons')
        else:
            load_buttons_tooltip = self.view_handler.get_tooltip('load_corpus_button')
        load_as_corpus_row: Row = Row(self.load_as_corpus_button, load_buttons_tooltip)
        self.load_as_meta_button: Button = Button(name='Load as metadata', width=130, button_style='outline',
                                                  button_type='success', visible=include_meta_loader)
        self.load_as_meta_button.on_click(self.load_as_meta)

        self.unload_selected_button: Button = Button(name="Unload selected", width=130, button_style='outline',
                                                     button_type='danger', disabled=True, align='end')
        self.unload_selected_button.on_click(self.unload_selected)
        self.unload_all_button: Button = Button(name="Unload all", width=130, button_style='solid',
                                                button_type='danger', disabled=True, align='end')
        self.unload_all_button.on_click(self.unload_all)
        self.unload_col: Column = Column(self.unload_selected_button, self.unload_all_button)

        self.loaded_file_info = Markdown()

        header_options = {'Yes': 'header', 'No': 'no_header', 'Infer': 'infer'}
        self.header_strategy_selector = Select(name='First row is header', options=header_options, width=100)
        self.header_strategy_selector.param.watch(self._on_header_strategy_update, ['value'])
        header_dropdown_tooltip = self.view_handler.get_tooltip('header_dropdown')

        self.corpus_name_input = TextInput(placeholder='Corpus name', width=130)
        self.build_button: Button = Button(name='Build corpus', button_style='solid', button_type='success', width=100)
        self.build_button.on_click(self.build_corpus)
        build_tool_tip: TooltipIcon = self.view_handler.get_tooltip('build_button')
        self.build_button_row: Row = Row(self.corpus_name_input, self.build_button, build_tool_tip,
                                         visible=False, align='start')

        self.file_selector = FileSelectorWidget(view_handler, controller, width=self.LOADER_WIDTH)
        self.file_selector.set_button_operation_fn(self._set_button_status_on_operation)
        self.meta_editor = MetaEditorWidget(view_handler, controller)

        self.panel = Row(
            Column(
                self.file_selector,
                Row(Column(
                    load_as_corpus_row,
                    self.load_as_meta_button
                ),
                    Row(self.header_strategy_selector,
                        header_dropdown_tooltip
                        ),
                    self.loaded_file_info,
                    HSpacer(),
                    self.unload_col,
                    width=self.LOADER_WIDTH),
                self.build_button_row,
                Row(self.controller.get_build_progress_bar())
            ),
            Spacer(width=50),
            self.meta_editor)
        self.children = [self.file_selector, self.meta_editor]
        self.update_display()

    def update_display(self):
        self._set_build_buttons_status()
        self.loaded_file_info.object = self.get_loaded_file_info()

    def get_loaded_file_info(self) -> str:
        file_counts: dict[str, int] = self.controller.get_loaded_file_counts()
        count_str: str = ""
        for filetype in file_counts:
            count_str += f"{filetype}: {file_counts[filetype]}\n"

        return count_str

    def _on_header_strategy_update(self, *_):
        strategy_value: str = self.header_strategy_selector.value
        self.controller.set_header_strategy(strategy_value)

    def _set_build_buttons_status(self, *_):
        files_added: bool = self.controller.is_meta_added() or self.controller.is_corpus_added()
        self.build_button_row.visible = files_added
        self.unload_selected_button.disabled = not files_added
        self.unload_all_button.disabled = not files_added
        self.header_strategy_selector.disabled = files_added

    def _set_button_status_on_operation(self, curr_loading: bool, *_):
        curr_loading = False  # TODO: Remove this line - temporary fix for https://github.com/holoviz/panel/issues/7389

        self.file_selector.selector_widget.disabled = curr_loading
        self.file_selector.show_hidden_files_checkbox.disabled = curr_loading
        self.file_selector.expand_archive_checkbox.disabled = curr_loading
        self.file_selector.select_all_button.disabled = curr_loading
        self.file_selector.file_type_filter.disabled = curr_loading
        self.file_selector.filter_input.disabled = curr_loading

        self.load_as_corpus_button.disabled = curr_loading
        self.load_as_meta_button.disabled = curr_loading
        self.build_button.disabled = curr_loading

    def load_as_corpus(self, *_):
        self._set_button_status_on_operation(curr_loading=True)
        include_hidden: bool = self.file_selector.get_show_hidden_value()
        file_ls: list[str] = self.file_selector.get_selector_value()
        self.view_handler.load_corpus_from_filepaths(file_ls, include_hidden)
        self._set_button_status_on_operation(curr_loading=False)

    def load_as_meta(self, *_):
        self._set_button_status_on_operation(curr_loading=True)
        include_hidden: bool = self.file_selector.get_show_hidden_value()
        file_ls: list[str] = self.file_selector.get_selector_value()
        self.view_handler.load_meta_from_filepaths(file_ls, include_hidden)
        self._set_button_status_on_operation(curr_loading=False)

    def unload_selected(self, *_):
        self._set_button_status_on_operation(curr_loading=True)
        file_ls: list[str] = self.file_selector.get_selector_value()
        self.controller.unload_filepaths(file_ls)
        self.view_handler.update_displays()
        self._set_button_status_on_operation(curr_loading=False)

    def unload_all(self, *_):
        self._set_button_status_on_operation(curr_loading=True)
        self.controller.unload_all()
        self.view_handler.update_displays()
        self._set_button_status_on_operation(curr_loading=False)

    def build_corpus(self, *_):
        self._set_button_status_on_operation(curr_loading=True)
        success: bool = self.view_handler.build_corpus(self.corpus_name_input.value_input)
        if success:
            self.corpus_name_input.value_input = ""
            self.corpus_name_input.value = ""
            self.unload_all()
        self._set_button_status_on_operation(curr_loading=False)
