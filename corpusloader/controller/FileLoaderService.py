import os
from typing import Optional

from atap_corpus.corpus.corpus import DataFrameCorpus
from pandas import DataFrame, merge, concat

from corpusloader.controller.data_objects import FileReference, CorpusHeader, ZipFileReference
from corpusloader.controller.file_loader_strategy import FileLoaderStrategy, FileLoaderFactory, FileLoadError


class FileLoaderService:
    def __init__(self):
        self.corpus_filepaths: list[FileReference] = []
        self.meta_filepaths: list[FileReference] = []

    def get_loaded_corpus_files(self) -> list[FileReference]:
        return self.corpus_filepaths.copy()

    def get_loaded_meta_files(self) -> list[FileReference]:
        return self.meta_filepaths.copy()

    def add_corpus_filepath(self, corpus_filepath: FileReference):
        if corpus_filepath in self.corpus_filepaths:
            return

        FileLoaderService._check_filepath_permissions(corpus_filepath)
        self.corpus_filepaths.append(corpus_filepath)

    def add_meta_filepath(self, meta_filepath: FileReference):
        if meta_filepath in self.meta_filepaths:
            return

        FileLoaderService._check_filepath_permissions(meta_filepath)
        self.meta_filepaths.append(meta_filepath)

    def remove_corpus_filepath(self, corpus_filepath: FileReference):
        if corpus_filepath in self.corpus_filepaths:
            self.corpus_filepaths.remove(corpus_filepath)

    def remove_meta_filepath(self, meta_filepath: FileReference):
        if meta_filepath in self.meta_filepaths:
            self.meta_filepaths.remove(meta_filepath)

    def remove_all_files(self):
        self.corpus_filepaths = []
        self.meta_filepaths = []

    def get_inferred_corpus_headers(self) -> list[CorpusHeader]:
        return FileLoaderService._get_file_headers(self.corpus_filepaths)

    def get_inferred_meta_headers(self) -> list[CorpusHeader]:
        return FileLoaderService._get_file_headers(self.meta_filepaths)

    def build_corpus(self, corpus_name: str,
                     corpus_headers: list[CorpusHeader],
                     meta_headers: list[CorpusHeader],
                     text_header: CorpusHeader,
                     corpus_link_header: Optional[CorpusHeader],
                     meta_link_header: Optional[CorpusHeader]) -> DataFrameCorpus:
        corpus_df: DataFrame = FileLoaderService._get_concatenated_dataframe(self.corpus_filepaths, corpus_headers)
        meta_df: DataFrame = FileLoaderService._get_concatenated_dataframe(self.meta_filepaths, meta_headers)

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
    def _check_filepath_permissions(file_ref: FileReference):
        filepath: str
        if file_ref.is_zipped():
            filepath = file_ref.get_directory_path()
        else:
            filepath = file_ref.get_full_path()
        if not os.path.exists(filepath):
            raise FileLoadError(f"No file found at: {filepath}")
        if not os.access(filepath, os.R_OK):
            raise FileLoadError(f"No permissions to read the file at: {filepath}")

    @staticmethod
    def _get_file_headers(file_refs: list[FileReference]) -> list[CorpusHeader]:
        headers: Optional[list[CorpusHeader]] = None
        for ref in file_refs:
            file_loader: FileLoaderStrategy = FileLoaderFactory.get_file_loader(ref)
            path_headers: list[CorpusHeader] = file_loader.get_inferred_headers()

            if headers is None:
                headers = path_headers
            elif set(headers) != set(path_headers):
                raise FileLoadError(f"Incompatible headers within loaded files")

        if headers is None:
            headers = []

        return headers

    @staticmethod
    def _get_concatenated_dataframe(file_refs: list[FileReference], headers: list[CorpusHeader]) -> DataFrame:
        if len(file_refs) == 0:
            return DataFrame()
        df_list: list[DataFrame] = []
        for ref in file_refs:
            file_loader: FileLoaderStrategy = FileLoaderFactory.get_file_loader(ref)
            try:
                path_df: DataFrame = file_loader.get_dataframe(headers)
            except Exception as e:
                raise FileLoadError(e)

            df_list.append(path_df)

        return concat(df_list, ignore_index=True)
