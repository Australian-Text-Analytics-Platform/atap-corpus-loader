from typing import Optional

from panel import Column, GridBox, bind, Row, Spacer
from panel.pane import Markdown, Str
from panel.widgets import Select, Checkbox, Button

from atap_corpus_loader.controller import Controller
from atap_corpus_loader.controller.data_objects.CorpusHeader import CorpusHeader
from atap_corpus_loader.view import ViewWrapperWidget
from atap_corpus_loader.view.gui import AbstractWidget


class MetaEditorWidget(AbstractWidget):
    TABLE_BORDER_STYLE = {'border': '1px dashed black', 'border-radius': '5px'}
    ERROR_BORDER_STYLE = {'border': '1px solid red', 'border-radius': '5px'}
    HEADER_STYLE = {'margin-top': '0', 'margin-bottom': '0', 'max-width': '150px'}
    MAX_HEADER_LENGTH: int = 80

    def __init__(self, view_handler: ViewWrapperWidget, controller: Controller):
        super().__init__()
        self.view_handler: ViewWrapperWidget = view_handler
        self.controller: Controller = controller

        self.corpus_table_container = GridBox(styles=MetaEditorWidget.TABLE_BORDER_STYLE)
        self.meta_table_container = GridBox(styles=MetaEditorWidget.TABLE_BORDER_STYLE)

        corpus_table_title = Markdown("## Corpus editor")
        corpus_table_tooltip = self.view_handler.get_tooltip('corpus_editor')
        self.corpus_table_row: Row = Row(corpus_table_tooltip, corpus_table_title)

        self.text_header_dropdown = Select(name='Document label', width=130)
        self.corpus_checkboxes: list[Checkbox] = []
        self.corpus_include_all_Button = Button(name="Include all", button_style='outline', button_type='success', align='end')
        self.corpus_include_all_Button.on_click(lambda e: self._toggle_all_corpus(True))
        self.corpus_exclude_all_Button = Button(name="Exclude all", button_style='outline', button_type='primary', align='end')
        self.corpus_exclude_all_Button.on_click(lambda e: self._toggle_all_corpus(False))

        meta_table_title = Markdown("## Metadata editor")
        meta_table_tooltip = self.view_handler.get_tooltip('meta_editor')
        self.meta_table_row: Row = Row(meta_table_tooltip, meta_table_title)
        self.meta_checkboxes: list[Checkbox] = []
        self.meta_include_all_button = Button(name="Include all", button_style='outline', button_type='success')
        self.meta_include_all_button.on_click(lambda e: self._toggle_all_meta(True))
        self.meta_exclude_all_button = Button(name="Exclude all", button_style='outline', button_type='primary')
        self.meta_exclude_all_button.on_click(lambda e: self._toggle_all_meta(False))

        self.link_row = Row(visible=False, styles=MetaEditorWidget.ERROR_BORDER_STYLE)
        link_row_tooltip = self.view_handler.get_tooltip('linking_selectors')
        self.corpus_link_dropdown = Select(name='Corpus linking label', width=150)
        self.meta_link_dropdown = Select(name='Metadata linking label', width=150)
        link_emoji = '\U0001F517'
        self.link_markdown = Str(link_emoji, styles={"font-size": "2em", "margin": "auto"})
        self.link_row.objects = [link_row_tooltip,
                                 self.corpus_link_dropdown,
                                 self.link_markdown.clone(),
                                 self.meta_link_dropdown]

        self.corpus_editor_control_row = Row(self.corpus_include_all_Button, self.corpus_exclude_all_Button, self.text_header_dropdown, visible=False)
        self.meta_editor_control_row = Row(self.meta_include_all_button, self.meta_exclude_all_button, visible=False)

        text_header_fn = bind(self._set_text_header, self.text_header_dropdown)
        corpus_link_fn = bind(self._set_corpus_link_header, self.corpus_link_dropdown)
        meta_link_fn = bind(self._set_meta_link_header, self.meta_link_dropdown)
        self.panel = Column(
            self.corpus_table_row,
            self.corpus_editor_control_row,
            self.corpus_table_container,
            Spacer(height=20),
            self.link_row,
            Spacer(height=20),
            self.meta_table_row,
            self.meta_editor_control_row,
            self.meta_table_container,
            text_header_fn, corpus_link_fn, meta_link_fn
        )
        self.update_display()

    def update_display(self):
        self._build_corpus_table()
        self._build_meta_table()
        self._update_dropdowns()

    def _toggle_all_corpus(self, state: bool, *_):
        for checkbox in self.corpus_checkboxes:
            if not checkbox.disabled:
                checkbox.value = state

    def _toggle_all_meta(self, state: bool, *_):
        for checkbox in self.meta_checkboxes:
            if not checkbox.disabled:
                checkbox.value = state

    def _set_text_header(self, text_header_name: Optional[str]):
        self.controller.set_text_header(text_header_name)
        self.update_display()

    def _set_corpus_link_header(self, header_name: str):
        self.controller.set_corpus_link_header(header_name)
        self.update_display()

    def _set_meta_link_header(self, header_name: str):
        self.controller.set_meta_link_header(header_name)
        self.update_display()

    def _get_table_cells_list(self, headers: list[CorpusHeader], link_header: CorpusHeader, is_meta_table: bool) -> tuple[int, list]:
        all_datatypes: list[str] = self.controller.get_all_datatypes()
        text_header: Optional[CorpusHeader] = self.controller.get_text_header()

        if is_meta_table:
            self.meta_checkboxes = []
        else:
            self.corpus_checkboxes = []

        table_cells: list = [Markdown('**Data label**', align='start'),
                             Markdown('**Datatype**', align='start'),
                             Markdown('**Include**', align='center')]
        if self.controller.is_meta_added():
            table_cells.append(Markdown('**Link**', align='center'))
        ncols: int = len(table_cells)

        for i, header in enumerate(headers):
            is_text = (header == text_header) and (not is_meta_table)
            is_link = (header == link_header)

            if is_link:
                header.include = True

            header_name_truncated: str = header.name[:MetaEditorWidget.MAX_HEADER_LENGTH]
            table_cells.append(Markdown(header_name_truncated, align='start', styles=MetaEditorWidget.HEADER_STYLE))

            datatype_selector = Select(options=all_datatypes, value=header.datatype.name, width=100, disabled=is_text)
            if is_meta_table:
                dtype_fn = bind(self.controller.update_meta_header, header, None, datatype_selector)
            else:
                dtype_fn = bind(self.controller.update_corpus_header, header, None, datatype_selector)
            table_cells.append(Row(datatype_selector, Column(dtype_fn, visible=False)))

            include_checkbox = Checkbox(value=header.include, align='center', disabled=(is_text or is_link))
            if is_meta_table:
                self.meta_checkboxes.append(include_checkbox)
                include_fn = bind(self.controller.update_meta_header, header, include_checkbox, None)
            else:
                self.corpus_checkboxes.append(include_checkbox)
                include_fn = bind(self.controller.update_corpus_header, header, include_checkbox, None)
            table_cells.append(Row(include_checkbox, Column(include_fn, visible=False)))

            if self.controller.is_meta_added():
                if is_link:
                    link_identifier = self.link_markdown.clone()
                else:
                    link_identifier = ' '
                table_cells.append(link_identifier)

        return ncols, table_cells

    def _build_corpus_table(self):
        is_corpus_added = self.controller.is_corpus_added()
        self.corpus_table_row.visible = is_corpus_added
        self.corpus_editor_control_row.visible = is_corpus_added
        self.corpus_table_container.visible = is_corpus_added

        corpus_headers: list[CorpusHeader] = self.controller.get_corpus_headers()
        link_header: Optional[CorpusHeader] = self.controller.get_corpus_link_header()

        ncols, corpus_table_cells = self._get_table_cells_list(corpus_headers, link_header, False)

        self.corpus_table_container.objects = corpus_table_cells
        self.corpus_table_container.ncols = ncols

    def _build_meta_table(self):
        is_meta_added = self.controller.is_meta_added()
        self.meta_table_row.visible = is_meta_added
        self.meta_editor_control_row.visible = is_meta_added
        self.meta_table_container.visible = is_meta_added

        meta_headers: list[CorpusHeader] = self.controller.get_meta_headers()
        link_header: Optional[CorpusHeader] = self.controller.get_meta_link_header()

        ncols, meta_table_cells = self._get_table_cells_list(meta_headers, link_header, True)

        self.meta_table_container.objects = meta_table_cells
        self.meta_table_container.ncols = ncols

    def _update_dropdowns(self):
        is_meta_added = self.controller.is_meta_added()
        is_corpus_added = self.controller.is_corpus_added()
        self.link_row.visible = is_meta_added
        self.text_header_dropdown.visible = is_corpus_added

        corpus_headers: list[CorpusHeader] = self.controller.get_corpus_headers()
        meta_headers: list[CorpusHeader] = self.controller.get_meta_headers()
        text_header: Optional[CorpusHeader] = self.controller.get_text_header()
        corpus_link_header: Optional[CorpusHeader] = self.controller.get_corpus_link_header()
        meta_link_header: Optional[CorpusHeader] = self.controller.get_meta_link_header()

        self.text_header_dropdown.options = [h.name for h in corpus_headers]
        if text_header is not None:
            self.text_header_dropdown.value = text_header.name

        self.corpus_link_dropdown.options = [''] + [h.name for h in corpus_headers]
        if corpus_link_header is None:
            self.corpus_link_dropdown.value = ''
        else:
            self.corpus_link_dropdown.value = corpus_link_header.name

        self.meta_link_dropdown.options = [''] + [h.name for h in meta_headers]
        if meta_link_header is None:
            self.meta_link_dropdown.value = ''
        else:
            self.meta_link_dropdown.value = meta_link_header.name

        if (meta_link_header is None) or (corpus_link_header is None):
            self.link_row.styles = MetaEditorWidget.ERROR_BORDER_STYLE
        else:
            self.link_row.styles = {}
