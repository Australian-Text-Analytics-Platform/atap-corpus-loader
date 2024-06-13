from typing import Optional, Callable

import panel
from atap_corpus._types import TCorpora
from atap_corpus.corpus.corpus import DataFrameCorpus
from panel.theme import Fast
from panel.viewable import Viewer, Viewable

from atap_corpus_loader.controller import Controller
from atap_corpus_loader.view import ViewWrapperWidget

panel.extension(notifications=True, design=Fast)


class CorpusLoader(Viewer):
    """
    Public interface for the CorpusLoader module. Maintains a reference to the logic Controller and the GUI wrapper.
    A CorpusLoader object can be used as a Panel component, i.e. will render in a Panel GUI.
    The build_callback_fn will be called when a corpus is built (can be set using set_build_callback()).
    """

    def __init__(self, root_directory: str, include_meta_loader: bool = False, **params):
        """
        :param root_directory: The root directory that the file selector will search for files to load. The argument must be a string. The directory may be non-existent at initialisation time, but no files will be displayed until it exists.
        :param include_meta_loader: If True, the Corpus Loader will include additional metadata joining functionality. False by default
        :param params: passed onto the panel.viewable.Viewer super-class
        :type root_directory: str
        :type include_meta_loader: bool
        """
        super().__init__(**params)
        self.controller: Controller = Controller(root_directory)
        self.view: ViewWrapperWidget = ViewWrapperWidget(self.controller, include_meta_loader)

    def __panel__(self):
        return self.view

    def add_tab(self, new_tab_name: str, new_tab_panel: Viewable):
        """
        Allows adding a Panel Viewable instance to the tab controls of the loader.
        :param new_tab_name: The name of the tab that will appear on the tab control bar
        :type new_tab_name: str
        :param new_tab_panel: The pane to attach to the new tab
        :type new_tab_panel: panel.viewable.Viewable
        """
        self.view.add_tab(new_tab_name, new_tab_panel)

    def set_build_callback(self, callback: Callable):
        """
        Allows a callback function to be set when a corpus has completed building.
        When the function is called, the only argument passed will be the built corpus object.
        :param callback: the function to call when a corpus has been built
        :type callback: Callable
        """
        self.controller.set_build_callback(callback)

    def get_latest_corpus(self) -> Optional[DataFrameCorpus]:
        """
        :return: the last DataFrameCorpus object that was built. If none have been built, returns None.
        :rtype: Optional[DataFrameCorpus]
        """
        return self.controller.get_latest_corpus()

    def get_corpus(self, corpus_name: str) -> Optional[DataFrameCorpus]:
        """
        :return: the DataFrameCorpus corresponding to the provided name. If no corpus with the given name is found, return None
        :rtype: Optional[DataFrameCorpus]
        """
        return self.controller.get_corpus(corpus_name)

    def get_corpora(self) -> dict[str, DataFrameCorpus]:
        """
        :return: a dictionary that maps Corpus names to DataFrameCorpus objects that have been built using this CorpusLoader
        :rtype: dict[str, DataFrameCorpus]
        """
        return self.controller.get_corpora()

    def get_mutable_corpora(self) -> TCorpora:
        """
        Returns the corpora object that contains the loaded corpus objects.
        This allows adding to the corpora from outside the CorpusLoader as the object returned is mutable, not a copy.
        The Corpora object has a unique name constraint, meaning a corpus object cannot be added to the corpora if another
        corpus with the same name is already present. The same constraint applies to the rename method of corpus objects
        added to the corpora.
        :return: the mutable corpora object that contains the loaded corpus objects
        :rtype: TCorpora
        """
        return self.controller.get_mutable_corpora()


