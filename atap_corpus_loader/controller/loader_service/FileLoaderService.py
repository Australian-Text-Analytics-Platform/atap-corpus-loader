from glob import iglob
from os import R_OK, access
from os.path import normpath, sep, isdir, exists
from typing import Iterator
from zipfile import BadZipFile

from panel.widgets import Tqdm

from atap_corpus_loader.controller.data_objects import FileReference
from atap_corpus_loader.controller.loader_service.FileLoadError import FileLoadError
from atap_corpus_loader.controller.loader_service.LoaderService import LoaderService


class FileLoaderService(LoaderService):
    """
    Provides methods that handle the logic of loading files and building the DataFrameCorpus object from the loaded
    files.
    Maintains a reference to files loaded as corpus files and files loaded as metadata files.
    """
    def __init__(self, root_directory: str):
        super().__init__()
        self.root_directory: str = self._sanitise_root_dir(root_directory)

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
                try:
                    zip_refs: list[FileReference] = self.file_ref_factory.get_zip_file_refs(filepath)
                except BadZipFile:
                    raise FileLoadError(f"Can't read Zip file as it is malformed: {file_ref.get_filename()}")
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
                try:
                    zip_refs: list[FileReference] = self.file_ref_factory.get_zip_file_refs(filepath)
                except BadZipFile:
                    raise FileLoadError(f"Can't read Zip file as it is malformed: {file_ref.get_filename()}")
                for zip_ref in zip_refs:
                    if not zip_ref.is_hidden() or include_hidden:
                        self.loaded_meta_files.add(zip_ref)

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
