import panel
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
