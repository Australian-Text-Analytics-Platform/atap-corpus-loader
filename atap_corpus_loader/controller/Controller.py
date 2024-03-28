import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from io import BytesIO
from os.path import abspath, join, dirname
from typing import Optional, Callable

from atap_corpus.corpus.corpus import DataFrameCorpus
from pandas import DataFrame
from panel.widgets import Tqdm

from atap_corpus_loader.controller.CorpusExportService import CorpusExportService
from atap_corpus_loader.controller.FileLoaderService import FileLoaderService, FileLoadError
from atap_corpus_loader.controller.OniAPIService import OniAPIService
from atap_corpus_loader.controller.data_objects import (FileReference, ViewCorpusInfo, CorpusHeader, DataType,
                                                        UniqueNameCorpora)
from atap_corpus_loader.controller.file_loader_strategy.FileLoaderFactory import ValidFileType
from atap_corpus_loader.view.notifications import NotifierService


class Controller:
    LOGGER: logging.Logger = None
    """
    Provides methods for indirection between the corpus loading logic and the user interface
    Holds a reference to the latest corpus built.
    The build_callback_fn will be called when a corpus is built (can be set using set_build_callback()).
    """
    def __init__(self, root_directory: str):
        Controller.setup_logger()

        self.file_loader_service: FileLoaderService = FileLoaderService(root_directory)
        self.oni_api_service: OniAPIService = OniAPIService()
        self.corpus_export_service: CorpusExportService = CorpusExportService()
        self.notifier_service: NotifierService = NotifierService()

        self.text_header: Optional[CorpusHeader] = None
        self.corpus_link_header: Optional[CorpusHeader] = None
        self.meta_link_header: Optional[CorpusHeader] = None

        self.corpus_headers: list[CorpusHeader] = []
        self.meta_headers: list[CorpusHeader] = []

        self.corpora: UniqueNameCorpora = UniqueNameCorpora()

        self.build_callback_fn: Optional[Callable] = None
        self.build_callback_args: list = []
        self.build_callback_kwargs: dict = {}

        self.tqdm_obj = Tqdm()
        self.tqdm_obj.visible = False

    @staticmethod
    def setup_logger():
        if Controller.LOGGER is not None:
            return
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file_location = abspath(join(dirname(__file__), '..', 'log.txt'))
        # Max size is ~10MB with 1 backup, so a max size of ~20MB for log files
        max_bytes: int = 10000000
        backup_count: int = 1
        file_handler = RotatingFileHandler(log_file_location, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)

        Controller.LOGGER = logging.getLogger(__name__)
        Controller.LOGGER.setLevel(logging.DEBUG)
        Controller.LOGGER.addHandler(file_handler)
        Controller.LOGGER.addHandler(console_handler)

        Controller.LOGGER.info('Logger started')

    def display_error(self, error_msg: str):
        Controller.LOGGER.error(f"Error displayed: {error_msg}")
        self.notifier_service.notify_error(error_msg)

    def display_success(self, success_msg: str):
        Controller.LOGGER.info(f"Success displayed: {success_msg}")
        self.notifier_service.notify_success(success_msg)

    def set_build_callback(self, callback: Callable, *args, **kwargs):
        if not callable(callback):
            raise ValueError("Provided callback function must be a callable")
        self.build_callback_fn = callback
        self.build_callback_args = args
        self.build_callback_kwargs = kwargs

    def get_latest_corpus(self) -> Optional[DataFrameCorpus]:
        if len(self.corpora) == 0:
            return
        return self.corpora.items()[-1]

    def get_corpus(self, corpus_name: str) -> Optional[DataFrameCorpus]:
        return self.corpora.get(corpus_name)

    def get_corpora(self) -> dict[str, DataFrameCorpus]:
        corpora_list: list = self.corpora.items()
        corpora_dict: dict[str, DataFrameCorpus] = {}
        for corpus in corpora_list:
            corpora_dict[corpus.name] = corpus

        return corpora_dict

    def load_corpus_from_filepaths(self, filepath_ls: list[str], include_hidden: bool) -> bool:
        Controller.LOGGER.debug(f"Files loaded as corpus: {filepath_ls}")
        try:
            self.file_loader_service.add_corpus_files(filepath_ls, include_hidden, self.tqdm_obj)
            self.corpus_headers = self.file_loader_service.get_inferred_corpus_headers()
        except FileLoadError as e:
            self.display_error(str(e))
            self.unload_all()
            return False

        return True

    def load_meta_from_filepaths(self, filepath_ls: list[str], include_hidden: bool) -> bool:
        Controller.LOGGER.debug(f"Files loaded as meta: {filepath_ls}")
        try:
            self.file_loader_service.add_meta_files(filepath_ls, include_hidden, self.tqdm_obj)
            self.meta_headers = self.file_loader_service.get_inferred_meta_headers()
        except FileLoadError as e:
            self.display_error(str(e))
            self.unload_all()
            return False

        return True

    def build_corpus(self, corpus_name: str) -> bool:
        if self.is_meta_added():
            if (self.corpus_link_header is None) or (self.meta_link_header is None):
                self.display_error("Cannot build without link headers set. Select a corpus header and a meta header as linking headers in the dropdowns")
                return False

        if (corpus_name == '') or (corpus_name is None):
            corpus_name = f"Corpus-{datetime.now()}"

        self.tqdm_obj.visible = True
        try:
            corpus = self.file_loader_service.build_corpus(corpus_name, self.corpus_headers,
                                                           self.meta_headers, self.text_header,
                                                           self.corpus_link_header, self.meta_link_header,
                                                           self.tqdm_obj)
        except FileLoadError as e:
            Controller.LOGGER.exception("Exception while building corpus: ")
            self.display_error(str(e))
            self.tqdm_obj.visible = False
            return False
        except Exception as e:
            Controller.LOGGER.exception("Exception while building corpus: ")
            self.display_error(f"Unexpected error building corpus: {e}")
            self.tqdm_obj.visible = False
            return False

        try:
            self.corpora.add(corpus)
        except Exception as e:
            Controller.LOGGER.exception("Exception while adding corpus to corpora: ")
            self.display_error(str(e))
            self.tqdm_obj.visible = False
            return False

        try:
            if self.build_callback_fn is not None:
                self.build_callback_fn(*self.build_callback_args, **self.build_callback_kwargs)
        except Exception as e:
            Controller.LOGGER.exception("Exception while calling build callback: ")
            self.display_error(f"Build callback error: {e}")
            self.tqdm_obj.visible = False
            return False

        self.tqdm_obj.visible = False

        return True

    def get_corpora_info(self) -> list[ViewCorpusInfo]:
        corpora_info: list[ViewCorpusInfo] = []

        for corpus in self.corpora.items():
            corpus_df: DataFrame = corpus.to_dataframe()

            name: Optional[str] = corpus.name
            num_rows: int = len(corpus)
            headers: list[str] = []
            dtypes: list[str] = []
            dtype: str
            for header_name, dtype_obj in corpus_df.dtypes.items():
                try:
                    dtype = DataType(str(dtype_obj).lower()).name
                except ValueError:
                    dtype = DataType.TEXT.name
                dtypes.append(dtype)
                headers.append(str(header_name))
            first_row_data: list[str] = [str(x) for x in corpus_df.iloc[0]]

            corpora_info.append(ViewCorpusInfo(name, num_rows, headers, dtypes, first_row_data))

        return corpora_info

    def delete_corpus(self, corpus_name: str):
        self.corpora.remove(corpus_name)

    def rename_corpus(self, corpus_name: str, new_name: str):
        corpus: Optional[DataFrameCorpus] = self.corpora.get(corpus_name)
        if corpus is None:
            self.display_error(f"No corpus with name {corpus_name} found")
            return

        try:
            corpus.rename(new_name)
        except ValueError as e:
            self.display_error(str(e))

    def get_loaded_file_counts(self) -> dict[str, int]:
        corpus_file_set = set(self.file_loader_service.get_loaded_corpus_files())
        meta_file_set = set(self.file_loader_service.get_loaded_meta_files())
        file_set = corpus_file_set | meta_file_set

        file_counts: dict[str, int] = {"Total files": len(file_set)}
        for file_ref in file_set:
            extension = file_ref.get_extension().upper()
            if file_counts.get(extension) is None:
                file_counts[extension] = 1
            else:
                file_counts[extension] += 1

        return file_counts

    def unload_filepaths(self, filepath_ls: list[str]):
        for filepath in filepath_ls:
            self.file_loader_service.remove_meta_filepath(filepath)
            self.file_loader_service.remove_corpus_filepath(filepath)

        if len(self.file_loader_service.get_loaded_corpus_files()) == 0:
            self.text_header = None
            self.corpus_headers = []
            self.corpus_link_header = None
        if len(self.file_loader_service.get_loaded_meta_files()) == 0:
            self.meta_headers = []
            self.meta_link_header = None

    def unload_all(self):
        Controller.LOGGER.debug("All files unloaded")
        self.file_loader_service.remove_all_files()

        self.text_header = None
        self.corpus_headers = []
        self.meta_headers = []
        self.corpus_link_header = None
        self.meta_link_header = None

    def get_loaded_corpus_files(self) -> set[FileReference]:
        return self.file_loader_service.get_loaded_corpus_files_set()

    def get_loaded_meta_files(self) -> set[FileReference]:
        return self.file_loader_service.get_loaded_meta_files_set()

    def get_corpus_headers(self) -> list[CorpusHeader]:
        return self.corpus_headers

    def get_meta_headers(self) -> list[CorpusHeader]:
        return self.meta_headers

    def get_text_header(self) -> Optional[CorpusHeader]:
        return self.text_header

    def get_corpus_link_header(self) -> Optional[CorpusHeader]:
        return self.corpus_link_header

    def get_meta_link_header(self) -> Optional[CorpusHeader]:
        return self.meta_link_header

    def get_all_datatypes(self) -> list[str]:
        return [d.name for d in DataType]

    def get_valid_filetypes(self) -> list[str]:
        return [ft.name for ft in ValidFileType]

    def is_corpus_added(self) -> bool:
        return len(self.file_loader_service.get_loaded_corpus_files()) > 0

    def is_meta_added(self) -> bool:
        return len(self.file_loader_service.get_loaded_meta_files()) > 0

    def update_corpus_header(self, header: CorpusHeader, include: Optional[bool], datatype_name: Optional[str]):
        if include is not None:
            header.include = include
        if datatype_name is not None:
            header.datatype = DataType[datatype_name]

        for i, corpus_header in enumerate(self.corpus_headers):
            if header == corpus_header:
                self.corpus_headers[i] = header

    def update_meta_header(self, header: CorpusHeader, include: Optional[bool], datatype_name: Optional[str]):
        if include is not None:
            header.include = include
        if datatype_name is not None:
            header.datatype = DataType[datatype_name]

        for i, meta_header in enumerate(self.meta_headers):
            if header == meta_header:
                self.meta_headers[i] = header

    def set_text_header(self, text_header: Optional[str]):
        if text_header is None:
            self.text_header = None
            return

        for header in self.corpus_headers:
            if header.name == text_header:
                self.text_header = header
                header.datatype = DataType.TEXT
                header.include = True
                return

    def set_corpus_link_header(self, link_header_name: Optional[str]):
        for header in self.corpus_headers:
            if header.name == link_header_name:
                self.corpus_link_header = header
                header.include = True
                return
        self.corpus_link_header = None

    def set_meta_link_header(self, link_header_name: Optional[str]):
        for header in self.meta_headers:
            if header.name == link_header_name:
                self.meta_link_header = header
                header.include = True
                return
        self.meta_link_header = None

    def retrieve_all_files(self, expand_archived: bool) -> list[FileReference]:
        return self.file_loader_service.get_all_files(expand_archived)

    def get_export_types(self) -> list[str]:
        return self.corpus_export_service.get_filetypes()

    def export_corpus(self, corpus_name: str, filetype: str) -> Optional[BytesIO]:
        corpus: Optional[DataFrameCorpus] = self.corpora.get(corpus_name)
        if corpus is None:
            self.display_error(f"No corpus with name '{corpus_name}' found")
            return None

        try:
            return self.corpus_export_service.export(corpus.to_dataframe(), filetype)
        except ValueError as e:
            self.display_error(str(e))
