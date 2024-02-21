from typing import Optional, Callable

import panel
from atap_corpus.corpus.corpus import DataFrameCorpus
from panel.viewable import Viewer

from atap_corpus_loader.controller import Controller
from atap_corpus_loader.view import ViewWrapperWidget, NotifierService

panel.extension(notifications=True)


class CorpusLoader(Viewer):
    """
    Public interface for the CorpusLoader module. Maintains a reference to the logic Controller and the GUI wrapper.
    A CorpusLoader object can be used as a Panel component, i.e. will render in a Panel GUI.
    The build_callback_fn will be called when a corpus is built (can be set using set_build_callback()).
    """

    def __init__(self, root_directory: str, **params):
        """

        :param root_directory: The root directory that the file selector will search for files to load.
        The argument must be a string. The directory may be non-existent at initialisation time,
        but no files will be displayed until it exists.
        :type root_directory: str
        :param params: passed onto the panel.viewable.Viewer super-class
        """
        super().__init__(**params)
        self.controller: Controller = Controller(root_directory)
        self.view: ViewWrapperWidget = ViewWrapperWidget(self.controller)

    def __panel__(self):
        return self.view

    def set_build_callback(self, callback: Callable, *args, **kwargs):
        """
        Allows a callback function to be set when a corpus has completed building
        :param callback: the function to call when a corpus has been built
        :param args: positional arguments to pass onto the callback function
        :param kwargs: keyword arguments to pass onto the callback function
        """
        self.controller.set_build_callback(callback, *args, **kwargs)

    def get_corpus(self) -> Optional[DataFrameCorpus]:
        """
        :return: the last DataFrameCorpus object that was built. If none have been built, returns None.
        """
        return self.controller.get_latest_corpus()

    def get_corpora(self) -> list[DataFrameCorpus]:
        return self.controller.get_corpora()
