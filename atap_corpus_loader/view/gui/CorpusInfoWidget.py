from io import BytesIO
from typing import Optional

import panel
from panel import Row, Accordion, bind, HSpacer
from panel.pane import Markdown
from panel.widgets import Button, TextInput, FileDownload, Select

from atap_corpus_loader.controller import Controller
from atap_corpus_loader.controller.data_objects import ViewCorpusInfo
from atap_corpus_loader.view.gui import AbstractWidget

panel.extension()


class CorpusInfoWidget(AbstractWidget):
    def __init__(self, controller: Controller):
        super().__init__()
        self.controller: Controller = controller

        self.corpus_controls = Accordion(toggle=True, width=600)
        self.corpus_controls.header_background = "#FFFFFA"
        self.corpus_controls.active_header_background = "#7A8B99"
        self.corpus_controls.param.watch(self._update_corpus_display, 'active', onlychanged=False)

        self.corpus_display: Markdown = Markdown()

        self.panel = Row(self.corpus_controls, self.corpus_display)

    @staticmethod
    def _build_corpus_label(corpus_info: ViewCorpusInfo) -> str:
        name: Optional[str] = corpus_info.name
        if name is None:
            name = " "
        row_info: str = f"{corpus_info.num_rows} document"
        if corpus_info.num_rows != 1:
            row_info += 's'

        return f"{name} - {row_info}"

    @staticmethod
    def _build_header_markdown_table(corpus_info: ViewCorpusInfo) -> str:
        if len(corpus_info.headers) != len(corpus_info.dtypes):
            return " "

        header_row = "| " + " | ".join(corpus_info.headers) + " |"
        spacer_row = "| :-: " * len(corpus_info.headers) + "|"
        data_row = "| " + " | ".join(corpus_info.dtypes) + " |"

        header_table_text = f"{header_row}\n{spacer_row}\n{data_row}"
        return header_table_text

    def export_corpus(self, corpus_id: str, filetype: str) -> Optional[BytesIO]:
        return self.controller.export_corpus(corpus_id, filetype)

    def rename_corpus(self, corpus_id: str, name: str):
        self.controller.rename_corpus(corpus_id, name)
        self.update_display()

    def delete_corpus(self, corpus_id: str):
        self.controller.delete_corpus(corpus_id)
        self.update_display()

    def _update_corpus_display(self, *event):
        current_active: list[int] = self.corpus_controls.active
        if len(current_active) == 0:
            self.corpus_display.object = ' '
            self.corpus_display.visible = False
            return

        corpora_info: list[ViewCorpusInfo] = self.controller.get_corpora_info()
        active_idx: int = current_active[0]
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
                callback=bind(self.export_corpus, corpus_id=corpus_info.corpus_id, filetype=filetype_dropdown),
                button_type="primary", button_style="solid",
                height=30, width=100,
                align="center")

            def select_fn(event, name=corpus_info.name, export_button=corpus_export_button):
                filename: str = f"{name}.{event.new}"
                export_button.filename = filename
            filetype_dropdown.param.watch(select_fn, ['value'])

            rename_field: TextInput = TextInput(name="Rename corpus", value=corpus_info.name,
                                                align='center', width=150)
            rename_field.param.watch(lambda event, corpus_id=corpus_info.corpus_id: self.rename_corpus(corpus_id, event.new), ['value'])
            delete_button: Button = Button(name="Delete corpus", button_type="danger", align='center')
            delete_button.on_click(lambda event, corpus_id=corpus_info.corpus_id: self.delete_corpus(corpus_id))

            corpus_control_row = Row(rename_field, filetype_dropdown, corpus_export_button,
                                     HSpacer(), delete_button, name=label)
            corpus_controls_objs.append(corpus_control_row)

        self.corpus_controls.objects = []
        self.corpus_controls.objects = corpus_controls_objs
        self._update_corpus_display()
