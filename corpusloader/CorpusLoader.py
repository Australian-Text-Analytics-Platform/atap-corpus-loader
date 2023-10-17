from corpusloader.controller import Controller
from corpusloader.model.corpus import CorpusService
from corpusloader.view import ViewWrapper, NotifierService


class CorpusLoader:
    def __init__(self):
        self.controller: Controller = Controller(CorpusService(), NotifierService())
        self.view: ViewWrapper = ViewWrapper(self.controller)

    def run(self):
        return self.view.get_component().servable()
