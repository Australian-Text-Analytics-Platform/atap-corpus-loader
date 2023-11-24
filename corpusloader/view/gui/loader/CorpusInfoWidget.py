from pandas import DataFrame as PandasDataFrame
from panel import Column
from panel.pane import DataFrame as PanelDataFrame

from corpusloader.view import ViewWrapperWidget
from corpusloader.view.gui import AbstractWidget
from corpusloader.view.gui.styles import file_info_style


class CorpusInfoWidget(AbstractWidget):
    def __init__(self, view_handler: ViewWrapperWidget):
        super().__init__()
        self.view_handler: ViewWrapperWidget = view_handler

        self.corpus_df_display: PanelDataFrame = PanelDataFrame()

        self.component = Column(self.corpus_df_display, styles=file_info_style)

    def update_display(self):
        pass

    def clear_loaded_corpus(self):
        self.corpus_df_display.object = None

    def set_corpus_df(self, corpus_df: PandasDataFrame):
        self.corpus_df_display.object = corpus_df
