from panel import Column, GridBox
from panel.pane import Markdown
from panel.widgets import Select, Checkbox

from corpusloader.controller import Controller
from corpusloader.view.gui import AbstractWidget


class MetaEditorWidget(AbstractWidget):
    def __init__(self, view_handler: AbstractWidget, controller: Controller):
        super().__init__()
        self.view_handler: AbstractWidget = view_handler
        self.controller: Controller = controller

        self.corpus_table_container = GridBox()
        self.meta_table_container = GridBox()

        self.corpus_table_title = Markdown("## Corpus header editor")
        self.meta_table_title = Markdown("## Metadata header editor")

        self.text_header_dropdown = Select(name='Select text header', width=200)

        self.panel = Column(
            self.corpus_table_title,
            self.text_header_dropdown,
            self.corpus_table_container,
            self.meta_table_title,
            self.meta_table_container
        )
        self.update_display()

    def _build_corpus_table(self):
        is_corpus_added = self.controller.is_corpus_added()
        self.corpus_table_title.visible = is_corpus_added
        self.corpus_table_container.visible = is_corpus_added
        self.text_header_dropdown.visible = is_corpus_added

        if not is_corpus_added:
            return

        corpus_headers: list[str] = self.controller.get_corpus_headers()
        corpus_datatypes: list[str] = self.controller.get_corpus_datatypes()
        all_datatypes: list[str] = self.controller.get_all_datatypes()

        corpus_table_cells: list = [Markdown('**Header name**', align='start'),
                                    Markdown('**Datatype**', align='start'),
                                    Markdown('**Include**', align='center')]
        if self.controller.is_meta_added():
            corpus_table_cells.append(Markdown('**Metadata link**', align='center'))
        ncols: int = len(corpus_table_cells)

        header_style = {"margin-top": "0", "margin-bottom": "0"}
        for i, header in enumerate(corpus_headers):
            corpus_table_cells.append(Markdown(header, align='start', style=header_style))

            datatype_selector = Select(options=all_datatypes, value=corpus_datatypes[i], width=100)
            corpus_table_cells.append(datatype_selector)

            include_checkbox = Checkbox(value=True, align='center')
            corpus_table_cells.append(include_checkbox)
            if self.controller.is_meta_added():
                link_row = (i == 0)
                link_checkbox = Checkbox(value=link_row, align='center')
                corpus_table_cells.append(link_checkbox)

        self.corpus_table_container.objects = corpus_table_cells
        self.corpus_table_container.ncols = ncols

        self.text_header_dropdown.options = self.controller.get_corpus_headers()

    def _build_meta_table(self):
        is_meta_added = self.controller.is_meta_added()
        self.meta_table_title.visible = is_meta_added
        self.meta_table_container.visible = is_meta_added

        if not is_meta_added:
            return

        meta_headers: list[str] = self.controller.get_meta_headers()
        meta_datatypes: list[str] = self.controller.get_meta_datatypes()
        all_datatypes: list[str] = self.controller.get_all_datatypes()

        meta_table_cells: list = [Markdown('**Header name**', align='start'),
                                    Markdown('**Datatype**', align='start'),
                                    Markdown('**Include**', align='center'),
                                    Markdown('**Corpus link**', align='center')]
        ncols: int = len(meta_table_cells)

        header_style = {"margin-top": "0", "margin-bottom": "0"}
        for i, header in enumerate(meta_headers):
            meta_table_cells.append(Markdown(header, style=header_style))

            datatype_selector = Select(options=all_datatypes, value=meta_datatypes[i], width=100)
            meta_table_cells.append(datatype_selector)

            include_checkbox = Checkbox(value=True, align='center')
            meta_table_cells.append(include_checkbox)

            link_checkbox = Checkbox(value=False, align='center')
            meta_table_cells.append(link_checkbox)

        self.meta_table_container.objects = meta_table_cells
        self.meta_table_container.ncols = ncols

    def update_display(self):
        self._build_corpus_table()
        self._build_meta_table()
