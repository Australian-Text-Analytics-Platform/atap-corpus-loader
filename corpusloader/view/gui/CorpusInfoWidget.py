from panel import Column
from panel.pane import DataFrame as PanelDataFrame

from corpusloader.controller import Controller
from corpusloader.view.gui import AbstractWidget


class CorpusInfoWidget(AbstractWidget):
    def __init__(self, controller: Controller):
        super().__init__()
        self.controller: Controller = controller

        self.corpus_df_display: PanelDataFrame = PanelDataFrame()

        self.panel = Column(self.corpus_df_display)

    def update_display(self):
        self.corpus_df_display.object = self.controller.get_loaded_corpus_df()
