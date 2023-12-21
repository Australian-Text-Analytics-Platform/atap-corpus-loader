from typing import Optional

from panel import GridBox
from panel.pane import Markdown

from corpusloader.controller import Controller
from corpusloader.view.gui import AbstractWidget


class CorpusInfoWidget(AbstractWidget):
    def __init__(self, controller: Controller):
        super().__init__()
        self.controller: Controller = controller

        self.panel = GridBox(ncols=2)

    def update_display(self):
        corpus_info: Optional[dict[str, str]] = self.controller.get_corpus_info()
        if corpus_info is None:
            self.panel.objects = []
            return

        corpus_info_ls: list[Markdown] = []
        for title in corpus_info:
            corpus_info_ls.append(Markdown(f"**{title}:** {corpus_info[title]}"))

        self.panel.objects = corpus_info_ls
