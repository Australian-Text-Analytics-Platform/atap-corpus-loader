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

        self.panel = Accordion(toggle=True, min_width=700)
        self.panel.header_background = "#FFFFFA"
        self.panel.active_header_background = "#7A8B99"

    @staticmethod
    def _build_corpus_label(corpus_info: ViewCorpusInfo) -> str:
        name: Optional[str] = corpus_info.name
        if name is None:
            name = " "
        row_info: str = f"{corpus_info.num_rows} document"
        if corpus_info.num_rows != 1:
            row_info += 's'

        return f"{name} -- {row_info}"

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

    def update_display(self):
        corpora_info: list[ViewCorpusInfo] = self.controller.get_corpora_info()
        self.panel.objects = []
        if len(corpora_info) == 0:
            return

        accordion_objs: list[Row] = []
        for corpus_info in corpora_info:
            label: str = CorpusInfoWidget._build_corpus_label(corpus_info)
            header_markdown_table: str = CorpusInfoWidget._build_header_markdown_table(corpus_info)
            info_markdown: Markdown = Markdown(header_markdown_table)

            rename_field: TextInput = TextInput(name="Rename corpus", value=corpus_info.name, align='center')
            rename_field.param.watch(lambda event: self.rename_corpus(corpus_info.corpus_id, event.new), 'value')
            delete_button: Button = Button(name="Delete corpus", button_type="danger", align='center')
            delete_button.on_click(lambda x: self.delete_corpus(corpus_info.corpus_id))

            accordion_objs.append(Row(info_markdown, HSpacer(), rename_field, delete_button, name=label))

        self.panel.objects = accordion_objs
