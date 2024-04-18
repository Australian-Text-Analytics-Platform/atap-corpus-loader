from abc import abstractmethod, ABC
from datetime import datetime
from typing import Optional

from atap_corpus.corpus.corpus import DataFrameCorpus
from pandas import DataFrame, merge, concat
from panel.widgets import Tqdm

from atap_corpus_loader.controller.data_objects import FileReference, CorpusHeader, FileReferenceFactory
from atap_corpus_loader.controller.loader_service.FileLoadError import FileLoadError
from atap_corpus_loader.controller.loader_service.file_loader_strategy import FileLoaderStrategy, FileLoaderFactory

"""
Some methods in this module utilise Tqdm from the panel library, which breaks the Model-View separation.
This has been done out of necessity for a progress bar for particular operations.
The panel Tqdm is a wrapper for the standard tqdm module and can be replaced if needed.
"""


class LoaderService(ABC):
    def __init__(self):
        self.loaded_corpus_files: set[FileReference] = set()
        self.loaded_meta_files: set[FileReference] = set()
        # Utilise FileReferenceFactory.clear_cache() if memory overhead is raised as an issue.
        self.file_ref_factory: FileReferenceFactory = FileReferenceFactory()

    @abstractmethod
    def get_all_files(self, expand_archived: bool) -> list[FileReference]:
        raise NotImplementedError()

    @abstractmethod
    def add_corpus_files(self, corpus_filepaths: list[str], include_hidden: bool, tqdm_obj: Tqdm):
        raise NotImplementedError()

    @abstractmethod
    def add_meta_files(self, meta_filepaths: list[str], include_hidden: bool, tqdm_obj: Tqdm):
        raise NotImplementedError()

    def is_corpus_loaded(self) -> bool:
        return len(self.loaded_corpus_files) > 0

    def is_meta_loaded(self) -> bool:
        return len(self.loaded_meta_files) > 0

    def get_loaded_corpus_files(self) -> set[FileReference]:
        return set([f for f in self.loaded_corpus_files if not f.is_archive()])

    def get_loaded_meta_files(self) -> set[FileReference]:
        return set(f for f in self.loaded_meta_files if not f.is_archive())

    def remove_corpus_filepath(self, corpus_filepath: str):
        file_ref: FileReference = self.file_ref_factory.get_file_ref(corpus_filepath)
        if file_ref in self.loaded_corpus_files:
            self.loaded_corpus_files.remove(file_ref)

    def remove_meta_filepath(self, meta_filepath: str):
        file_ref: FileReference = self.file_ref_factory.get_file_ref(meta_filepath)
        if file_ref in self.loaded_meta_files:
            self.loaded_meta_files.remove(file_ref)

    def remove_loaded_corpus_files(self):
        self.loaded_corpus_files.clear()

    def remove_loaded_meta_files(self):
        self.loaded_meta_files.clear()

    def remove_all_files(self):
        self.remove_loaded_corpus_files()
        self.remove_loaded_meta_files()

    def get_inferred_corpus_headers(self) -> list[CorpusHeader]:
        return self._get_file_headers(self.get_loaded_corpus_files())

    def get_inferred_meta_headers(self) -> list[CorpusHeader]:
        return self._get_file_headers(self.get_loaded_meta_files())

    def _get_file_headers(self, file_refs: set[FileReference]) -> list[CorpusHeader]:
        headers: Optional[list[CorpusHeader]] = None
        for ref in file_refs:
            file_loader: FileLoaderStrategy = FileLoaderFactory.get_file_loader(ref)
            try:
                path_headers: list[CorpusHeader] = file_loader.get_inferred_headers()
            except UnicodeDecodeError:
                self.remove_corpus_filepath(ref.get_path())
                self.remove_meta_filepath(ref.get_path())
                raise FileLoadError(f"Error loading file at {ref.get_path()}: file is not UTF-8 encoded")
            except Exception as e:
                self.remove_corpus_filepath(ref.get_path())
                self.remove_meta_filepath(ref.get_path())
                raise FileLoadError(f"Error loading file at {ref.get_path()}: {e}")

            if headers is None:
                headers = path_headers
            elif set(headers) != set(path_headers):
                self.remove_corpus_filepath(ref.get_path())
                self.remove_meta_filepath(ref.get_path())
                raise FileLoadError(f"Incompatible data labels in file: {ref.get_path()}")

        if headers is None:
            headers = []

        return headers

    def build_corpus(self, corpus_name: str,
                     corpus_headers: list[CorpusHeader],
                     meta_headers: list[CorpusHeader],
                     text_header: CorpusHeader,
                     corpus_link_header: Optional[CorpusHeader],
                     meta_link_header: Optional[CorpusHeader],
                     tqdm_obj: Tqdm) -> DataFrameCorpus:
        corpus_files: list[FileReference] = sorted(self.get_loaded_corpus_files(), key=lambda f: f.get_path())
        meta_files: list[FileReference] = sorted(self.get_loaded_meta_files(), key=lambda f: f.get_path())

        corpus_df: DataFrame = self._get_concatenated_dataframe(corpus_files, corpus_headers,
                                                                tqdm_obj, "Building corpus")
        meta_df: DataFrame = self._get_concatenated_dataframe(meta_files, meta_headers,
                                                              tqdm_obj, "Building metadata")

        load_corpus: bool = len(corpus_headers) > 0
        load_meta: bool = len(meta_headers) > 0

        final_df: DataFrame
        if load_corpus and load_meta:
            final_df = merge(left=corpus_df, right=meta_df,
                             left_on=corpus_link_header.name, right_on=meta_link_header.name,
                             how='inner', suffixes=(None, '_meta'))
        elif load_corpus:
            final_df = corpus_df
        elif load_meta:
            final_df = meta_df
        else:
            raise ValueError("No corpus headers or metadata headers provided")

        if (corpus_name == '') or (corpus_name is None):
            corpus_name = f"Corpus-{datetime.now()}"

        return DataFrameCorpus.from_dataframe(final_df, text_header.name, corpus_name)

    @staticmethod
    def _get_concatenated_dataframe(file_refs: list[FileReference],
                                    headers: list[CorpusHeader],
                                    tqdm_obj: Tqdm,
                                    loading_msg: str) -> DataFrame:
        if len(file_refs) == 0:
            return DataFrame()
        df_list: list[DataFrame] = []
        for ref in tqdm_obj(file_refs, desc=loading_msg, unit="files", leave=False):
            file_loader: FileLoaderStrategy = FileLoaderFactory.get_file_loader(ref)
            try:
                path_df: DataFrame = file_loader.get_dataframe(headers)
            except UnicodeDecodeError:
                raise FileLoadError(f"Error loading file at {ref.get_path()}: file is not UTF-8 encoded")
            except Exception as e:
                raise FileLoadError(f"Error loading file at {ref.get_path()}: {e}")

            df_list.append(path_df)

        return concat(df_list, ignore_index=True)