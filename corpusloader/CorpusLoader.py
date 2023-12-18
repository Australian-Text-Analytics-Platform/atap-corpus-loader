from typing import Optional, Callable

import panel
from atap_corpus.corpus.corpus import DataFrameCorpus
from panel.viewable import Viewer

from corpusloader.controller import Controller
from corpusloader.view import ViewWrapperWidget, NotifierService

panel.extension(notifications=True)


class CorpusLoader(Viewer):
    def __init__(self, base_path: str, **params):
        super().__init__(**params)
        self.controller: Controller = Controller(NotifierService())
        self.view: ViewWrapperWidget = ViewWrapperWidget(self.controller, base_path)

    def __panel__(self):
        return self.view

    def set_build_callback(self, callback: Callable, *args, **kwargs):
        self.controller.set_build_callback(callback, *args, **kwargs)

    def get_corpus(self) -> Optional[DataFrameCorpus]:
        return self.controller.get_corpus()
