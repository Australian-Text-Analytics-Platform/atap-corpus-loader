from corpusloader.controller import Controller
from corpusloader.controller import CorpusService
from corpusloader.view import ViewWrapperWidget, NotifierService


class CorpusLoader:
    def __init__(self, base_path: str):
        self.controller: Controller = Controller(CorpusService(), NotifierService())
        self.view: ViewWrapperWidget = ViewWrapperWidget(self.controller, base_path)

    def run(self):
        return self.view.get_component().servable()
