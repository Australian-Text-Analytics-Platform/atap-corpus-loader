from panel import Column
from panel.pane import DataFrame as PanelDataFrame

from corpusloader.view import ViewWrapper
from corpusloader.view.gui import AbstractWidget


class DisplayWidget(AbstractWidget):
    def __init__(self, view_handler: ViewWrapper):
        self.view_handler: ViewWrapper = view_handler

        self.dataframe_viewer: PanelDataFrame = PanelDataFrame(index=False)

        self.component = Column(
            self.dataframe_viewer
        )

    def get_component(self):
        return self.component

    def update_displays(self):
        self.dataframe_viewer.object = self.view_handler.get_loaded_corpus_as_dataframe()

    def set_visibility(self, is_visible: bool):
        self.component.visible = is_visible

    def toggle_visibility(self):
        self.component.visible = not self.component.visible
