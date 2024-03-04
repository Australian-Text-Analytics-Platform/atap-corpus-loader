from glob import iglob
from os import R_OK, access
from os.path import normpath, sep, isdir, exists
from typing import Optional, Iterator

from atap_corpus.corpus.corpus import DataFrameCorpus
from pandas import DataFrame, merge, concat
from panel.widgets import Tqdm

from atap_corpus_loader.controller.data_objects import FileReference, CorpusHeader, FileReferenceFactory
from atap_corpus_loader.controller.file_loader_strategy import FileLoaderStrategy, FileLoaderFactory, FileLoadError

"""
Some methods in this module utilise Tqdm from the panel library, which breaks the Model-View separation.
This has been done out of necessity for a progress bar for particular operations.
The panel Tqdm is a wrapper for the standard tqdm module and can be replaced if needed.
"""


class FileLoaderService:
    """
    Provides methods that handle the logic of loading files and building the DataFrameCorpus object from the loaded
    files.
    Maintains a reference to files loaded as corpus files and files loaded as metadata files.
    """
    def __init__(self, root_directory: str):
        self.root_directory: str = self._sanitise_root_dir(root_directory)
        self.loaded_corpus_files: set[FileReference] = set()
        self.loaded_meta_files: set[FileReference] = set()
        # Utilise FileReferenceFactory.clear_cache() if memory overhead is raised as an issue.
        self.file_ref_factory: FileReferenceFactory = FileReferenceFactory()

        self.all_files_cache: list[FileReference] = []
        self.all_files_count: int = 0

    def get_all_files(self, expand_archived: bool) -> list[FileReference]:
        path_iter: Iterator = iglob(f"{self.root_directory}**", recursive=True)
        all_file_refs: list[FileReference] = []
        for path in path_iter:
            if isdir(path):
                continue

            file_refs: list[FileReference] = self.file_ref_factory.get_file_refs_from_path(path, expand_archived)
            all_file_refs.extend(file_refs)

        all_file_refs.sort(key=lambda ref: ref.get_path())

        return all_file_refs

    def get_loaded_corpus_files(self) -> list[FileReference]:
        return [f for f in self.loaded_corpus_files if not f.is_archive()]

    def get_loaded_meta_files(self) -> list[FileReference]:
        return [f for f in self.loaded_meta_files if not f.is_archive()]

    def get_loaded_corpus_files_set(self) -> set[FileReference]:
        return set(self.get_loaded_corpus_files())

    def get_loaded_meta_files_set(self) -> set[FileReference]:
        return set(self.get_loaded_meta_files())

    def add_corpus_files(self, corpus_filepaths: list[str], include_hidden: bool, tqdm_obj: Tqdm):
        for filepath in tqdm_obj(corpus_filepaths, desc="Loading corpus files", unit="files", leave=False):
            file_ref: FileReference = self.file_ref_factory.get_file_ref(filepath)
            if file_ref in self.loaded_corpus_files:
                continue
            if not include_hidden and file_ref.is_hidden():
                continue
            FileLoaderService._check_filepath_permissions(file_ref)

            self.loaded_corpus_files.add(file_ref)
            if file_ref.is_archive():
                zip_refs: list[FileReference] = self.file_ref_factory.get_zip_file_refs(filepath)
                for zip_ref in zip_refs:
                    if not zip_ref.is_hidden() or include_hidden:
                        self.loaded_corpus_files.add(zip_ref)

    def add_meta_files(self, meta_filepaths: list[str], include_hidden: bool, tqdm_obj: Tqdm):
        for filepath in tqdm_obj(meta_filepaths, desc="Loading metadata files", unit="files", leave=False):
            file_ref: FileReference = self.file_ref_factory.get_file_ref(filepath)
            if file_ref in self.loaded_meta_files:
                continue
            if not include_hidden and file_ref.is_hidden():
                continue
            FileLoaderService._check_filepath_permissions(file_ref)

            self.loaded_meta_files.add(file_ref)
            if file_ref.is_archive():
                zip_refs: list[FileReference] = self.file_ref_factory.get_zip_file_refs(filepath)
                for zip_ref in zip_refs:
                    if not zip_ref.is_hidden() or include_hidden:
                        self.loaded_meta_files.add(zip_ref)

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

    def _get_file_headers(self, file_refs: list[FileReference]) -> list[CorpusHeader]:
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
        corpus_df: DataFrame = FileLoaderService._get_concatenated_dataframe(self.get_loaded_corpus_files(),
                                                                             corpus_headers,
                                                                             tqdm_obj,
                                                                             "Building corpus")
        meta_df: DataFrame = FileLoaderService._get_concatenated_dataframe(self.get_loaded_meta_files(),
                                                                           meta_headers,
                                                                           tqdm_obj,
                                                                           "Building metadata")

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

        return DataFrameCorpus.from_dataframe(df=final_df, col_doc=text_header.name, name=corpus_name)

    @staticmethod
    def _sanitise_root_dir(root_directory: str) -> str:
        if type(root_directory) is not str:
            raise TypeError(f"root_directory argument: expected string, got {type(root_directory)}")
        sanitised_directory = normpath(root_directory)

        if not sanitised_directory.endswith(sep):
            sanitised_directory += sep

        return sanitised_directory

    @staticmethod
    def _check_filepath_permissions(file_ref: FileReference):
        filepath: str
        if file_ref.is_zipped():
            filepath = file_ref.get_directory_path()
        else:
            filepath = file_ref.get_path()
        if not exists(filepath):
            raise FileLoadError(f"No file found at: {filepath}")
        if not access(filepath, R_OK):
            raise FileLoadError(f"No permissions to read the file at: {filepath}")

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
