from typing import Optional

import panel
from panel import Row, Accordion, HSpacer
from panel.pane import Markdown
from panel.widgets import Button, TextInput

from atap_corpus_loader.controller import Controller
from atap_corpus_loader.controller.data_objects import ViewCorpusInfo
from atap_corpus_loader.view.gui import AbstractWidget

panel.extension()


class CorpusInfoWidget(AbstractWidget):
    def __init__(self, controller: Controller):
        super().__init__()
        self.controller: Controller = controller

        self.corpus_controls = Accordion(toggle=True, min_width=700)
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

        header_row = "| " + " | ".join(corpus_info.headers)
        spacer_row = "| :-: " * len(corpus_info.headers) + "|"
        data_row = "| " + " | ".join(corpus_info.dtypes)

        header_table_text = f"{header_row}\n{spacer_row}\n{data_row}"
        return header_table_text

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
        corpus_display_text: str = f"**<div style='text-align: center;'>{corpus_info.name}</div>**\n\n{header_markdown_table}"

        self.corpus_display.object = corpus_display_text
        self.corpus_display.visible = True

    def update_display(self):
        corpora_info: list[ViewCorpusInfo] = self.controller.get_corpora_info()

        corpus_controls_objs: list[Row] = []
        for corpus_info in corpora_info:
            label: str = CorpusInfoWidget._build_corpus_label(corpus_info)

            rename_field: TextInput = TextInput(name="Rename corpus", value=corpus_info.name, align='center')
            rename_field.param.watch(lambda event, corpus_id=corpus_info.corpus_id: self.rename_corpus(corpus_id, event.new), ['value'])
            delete_button: Button = Button(name="Delete corpus", button_type="danger", align='center')
            delete_button.on_click(lambda event, corpus_id=corpus_info.corpus_id: self.delete_corpus(corpus_id))

            corpus_controls_objs.append(Row(rename_field, delete_button, name=label))

        self.corpus_controls.objects = corpus_controls_objs
        self._update_corpus_display()
