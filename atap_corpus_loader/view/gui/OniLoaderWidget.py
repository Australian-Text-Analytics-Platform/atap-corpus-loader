from panel import Row

from atap_corpus_loader.controller import Controller
from atap_corpus_loader.view.gui import AbstractWidget


class OniLoaderWidget(AbstractWidget):
    def __init__(self, controller: Controller):
        super().__init__()
        self.controller: Controller = controller

        self.panel = Row()

    def update_display(self):
        pass
