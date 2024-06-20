import re
from io import BytesIO
from typing import Optional

from panel import Row, Accordion, bind, HSpacer, Column
from panel.layout import Divider
from panel.pane import Markdown
from panel.widgets import Button, TextInput, FileDownload, Select

from atap_corpus_loader.controller import Controller
from atap_corpus_loader.controller.data_objects import ViewCorpusInfo
from atap_corpus_loader.view.gui import AbstractWidget


class CorpusInfoWidget(AbstractWidget):
    def __init__(self, controller: Controller):
        super().__init__()
        self.controller: Controller = controller

        self.corpus_controls = Accordion(toggle=True, width=600,
                                         header_background="#2675C3",
                                         active_header_background="#56AAFC")
        self.corpus_controls.param.watch(self._update_corpus_display, 'active', onlychanged=True)

        self.corpus_display: Markdown = Markdown()

        self.panel = Column(
            self.corpus_controls,
            Row(self.controller.get_export_progress_bar()),
            Divider(),
            self.corpus_display)

    @staticmethod
    def _build_corpus_label(corpus_info: ViewCorpusInfo) -> str:
        name: Optional[str] = corpus_info.name
        if name is None:
            name = " "
        corpus_label: str = f"{name} - {corpus_info.num_rows} document"
        if corpus_info.num_rows != 1:
            corpus_label += 's'
        if corpus_info.parent_name:
            corpus_label += f" - Parent: {corpus_info.parent_name}"

        return corpus_label

    @staticmethod
    def _build_header_markdown_table(corpus_info: ViewCorpusInfo) -> str:
        if len(corpus_info.headers) != len(corpus_info.dtypes):
            return " "

        sanitised_first_row: list[str] = [re.sub(r'([\\\`*_{}[\]()#+\-.!])', r'\\\1', x) for x in corpus_info.first_row_data]
        sanitised_first_row = [re.sub(r'([\n\r\n])', ' ', x) for x in sanitised_first_row]

        header_row = "| Data label " + "| " + " | ".join(corpus_info.headers) + " |"
        spacer_row = "| :-: " * (len(corpus_info.headers) + 1) + "|"
        dtype_row = "| **Datatype** " + "| " + " | ".join(corpus_info.dtypes) + " |"
        data_row = "| **First document** " + "| " + " | ".join(sanitised_first_row) + " |"

        header_table_text = f"**{corpus_info.name}**\n{header_row}\n{spacer_row}\n{dtype_row}\n{data_row}"
        return header_table_text

    def export_corpus(self, corpus_name: str, filetype: str) -> Optional[BytesIO]:
        return self.controller.export_corpus(corpus_name, filetype)

    def rename_corpus(self, corpus_name: str, name: str):
        self.controller.rename_corpus(corpus_name, name)
        self.update_display()

    def delete_corpus(self, corpus_name: str):
        self.controller.delete_corpus(corpus_name)
        self.update_display()

    def _update_corpus_display(self, *_):
        corpora_info: list[ViewCorpusInfo] = self.controller.get_corpora_info()
        if len(corpora_info) == 0:
            self.corpus_display.object = ' '
            self.corpus_display.visible = False
            return

        if len(self.corpus_controls.active) == 0:
            self.corpus_controls.active = [0]

        active_idx: int = self.corpus_controls.active[0]
        if active_idx >= len(corpora_info):
            self.corpus_display.object = ' '
            self.corpus_display.visible = False
            return

        corpus_info: ViewCorpusInfo = corpora_info[active_idx]
        header_markdown_table: str = CorpusInfoWidget._build_header_markdown_table(corpus_info)

        self.corpus_display.object = header_markdown_table
        self.corpus_display.visible = True

    def update_display(self):
        corpora_info: list[ViewCorpusInfo] = self.controller.get_corpora_info()
        export_types: list[str] = self.controller.get_export_types()
        default_filetype: str = export_types[0]

        corpus_controls_objs: list[Row] = []
        for corpus_info in corpora_info:
            label: str = CorpusInfoWidget._build_corpus_label(corpus_info=corpus_info)

            filetype_dropdown = Select(name="Export filetype", options=export_types, value=default_filetype,
                                       width=100, align="center")
            corpus_export_button = FileDownload(
                label=f"Export",
                filename=f"{corpus_info.name}.{default_filetype}",
                callback=bind(self.export_corpus, corpus_name=corpus_info.name, filetype=filetype_dropdown),
                button_type="primary", button_style="solid",
                height=30, width=100,
                align="center")

            def select_fn(event, name=corpus_info.name, export_button=corpus_export_button):
                filename: str = f"{name}.{event.new}"
                export_button.filename = filename
            filetype_dropdown.param.watch(select_fn, ['value'])

            rename_field: TextInput = TextInput(name="Rename corpus", value=corpus_info.name,
                                                align='center', width=150)
            rename_field.param.watch(lambda event, corpus_name=corpus_info.name: self.rename_corpus(corpus_name, event.new), ['value'])
            delete_button: Button = Button(name="Delete corpus", button_type="danger", align='center')
            delete_button.on_click(lambda event, corpus_name=corpus_info.name: self.delete_corpus(corpus_name))

            corpus_control_row = Row(rename_field, filetype_dropdown, corpus_export_button,
                                     HSpacer(), delete_button, name=label)
            corpus_controls_objs.append(corpus_control_row)

        self.corpus_controls.objects = []
        self.corpus_controls.objects = corpus_controls_objs
        self._update_corpus_display()
