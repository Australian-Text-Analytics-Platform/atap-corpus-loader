from typing import Optional

from panel import Column, Row
from panel.pane import Markdown

from corpusloader.controller import Controller
from corpusloader.view.gui import AbstractWidget


class CorpusInfoWidget(AbstractWidget):
    CONTAINER_STYLE = {'border': '1px dashed black', 'border-radius': '5px', 'min-width': '700px'}

    def __init__(self, controller: Controller):
        super().__init__()
        self.controller: Controller = controller

        self.panel = Column(styles=CorpusInfoWidget.CONTAINER_STYLE)
        self.panel.visible = False

    @staticmethod
    def _build_header_markdown_table(headers: list[str], dtypes: list[str]) -> Markdown:
        if len(headers) != len(dtypes):
            return Markdown(" ")

        title = "**Header data types**"
        header_row = "| " + " | ".join(headers)
        spacer_row = "| :-: " * len(headers) + "|"
        data_row = "| " + " | ".join(dtypes)

        header_table_text = f"{title}\n{header_row}\n{spacer_row}\n{data_row}"
        return Markdown(header_table_text)

    def update_display(self):
        corpus_info: Optional[dict] = self.controller.get_corpus_info()
        if corpus_info is None:
            self.panel.objects = []
            self.panel.visible = False
            return

        name: str = corpus_info.get('name')
        num_rows: str = corpus_info.get('rows')
        num_files: str = corpus_info.get('files')
        headers: list[str] = corpus_info.get('headers')
        dtypes: list[str] = corpus_info.get('dtypes')

        header_table = CorpusInfoWidget._build_header_markdown_table(headers, dtypes)
        corpus_info_ls: list = [Markdown(f"## {name} Overview"),
                                Row(Markdown(f"**{num_rows}** document row(s)"),
                                    Markdown(f"**{num_files}** source file(s)")),
                                header_table]

        self.panel.objects = corpus_info_ls
        self.panel.visible = True
