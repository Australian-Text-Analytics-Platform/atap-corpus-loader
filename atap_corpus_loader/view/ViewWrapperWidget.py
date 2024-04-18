from typing import Optional

from panel import Tabs
from panel.widgets import TooltipIcon

from atap_corpus_loader.controller import Controller
from atap_corpus_loader.view.gui import AbstractWidget, FileLoaderWidget, CorpusInfoWidget, OniLoaderWidget
from atap_corpus_loader.view.tooltips import TooltipManager


class ViewWrapperWidget(AbstractWidget):
    """
    A wrapper class that holds different loading method interfaces within a Tab
    """
    def __init__(self, controller: Controller, include_meta_loader: bool):
        super().__init__()
        self.controller: Controller = controller
        self.tooltip_manager: TooltipManager = TooltipManager()

        self.file_loader: FileLoaderWidget = FileLoaderWidget(self, controller, include_meta_loader)
        self.oni_loader: OniLoaderWidget = OniLoaderWidget(self, controller, include_meta_loader)
        self.corpus_display: CorpusInfoWidget = CorpusInfoWidget(controller)

        # set_load_service_type depends on the order of these tabs
        self.panel = Tabs(("File Loader", self.file_loader),
                          ("Oni Loader", self.oni_loader),
                          ("Corpus Overview", self.corpus_display))
        self.panel.param.watch(self.set_load_service_type, parameter_names=['active'])
        self.corpus_info_idx: int = len(self.panel) - 1
        self.children = [self.file_loader, self.oni_loader, self.corpus_display]

    def update_display(self):
        pass

    def load_corpus_from_filepaths(self, filepath_ls: list[str], include_hidden: bool):
        if len(filepath_ls) == 0:
            return
        success = self.controller.load_corpus_from_filepaths(filepath_ls, include_hidden)
        self.update_displays()
        if success:
            self.controller.display_success("Corpus files loaded successfully")

    def load_meta_from_filepaths(self, filepath_ls: list[str], include_hidden: bool):
        if len(filepath_ls) == 0:
            return
        success = self.controller.load_meta_from_filepaths(filepath_ls, include_hidden)
        self.update_displays()
        if success:
            self.controller.display_success("Metadata files loaded successfully")

    def build_corpus(self, corpus_id: str) -> bool:
        success: bool = self.controller.build_corpus(corpus_id)
        if success:
            self.update_displays()

            self.panel.active = self.corpus_info_idx
            corpus_id: str = self.controller.get_latest_corpus().name
            self.controller.display_success(f"Corpus {corpus_id} built successfully")

        return success

    def set_load_service_type(self, *_):
        active_tab: int = self.panel.active
        if active_tab == 0:
            self.controller.set_loader_service_type('file')
        elif active_tab == 1:
            self.controller.set_loader_service_type('oni')

    def get_tooltip(self, tooltip_name: str) -> Optional[TooltipIcon]:
        return self.tooltip_manager.get_tooltip(tooltip_name)
