import logging
from io import BytesIO
from typing import Optional

import requests
from atap_corpus.corpus.corpus import DataFrameCorpus
from panel.widgets import Tqdm

from atap_corpus_loader.controller.data_objects import FileReference
from atap_corpus_loader.controller.data_objects.FileReference import RemoteFileReference
from atap_corpus_loader.controller.loader_service import LoaderService
from atap_corpus_loader.controller.loader_service.FileLoadError import FileLoadError


class OniLoaderService(LoaderService):
    def __init__(self):
        super().__init__()
        self.providers: dict[str, str] = {"LDaCA": "https://data.ldaca.edu.au"}
        self.curr_provider: str = "LDaCA"
        self.api_key: Optional[str] = None
        self.collection_id: str = ''
        self.collection_files: list[FileReference] = []

    def _get_api_root(self) -> str:
        base_url: Optional[str] = self.providers.get(self.curr_provider)
        if base_url is None:
            return ''
        return base_url + '/api/'

    def _get_auth_header(self) -> dict:
        return {'Authorization': f"Bearer {self.api_key}"}

    def _validate_collection_id(self, collection_id: str) -> bool:
        if len(collection_id) == 0:
            return False

        return True

    def _validate_api_key(self, api_key: str) -> bool:
        if len(api_key) == 0:
            return False

        return True

    def set_provider(self, name: str, address: str):
        if name == '':
            raise ValueError("The name cannot be empty")
        if address == '':
            raise ValueError("The address cannot be empty")
        self.providers[name] = address

    def get_providers(self) -> list[str]:
        return list(self.providers.keys())

    def set_curr_provider(self, name: str):
        if name not in self.providers:
            raise ValueError(f"Provider '{name}' not found in providers list")
        self.curr_provider = name

    def get_curr_provider(self) -> str:
        return self.curr_provider

    def get_curr_provider_address(self) -> str:
        curr_address = self.providers.get(self.curr_provider)
        if curr_address:
            return curr_address
        return ''

    def set_api_key(self, api_key: str) -> bool:
        if self._validate_api_key(api_key):
            self.api_key = api_key
            return True
        return False

    def set_collection_id(self, collection_id: str):
        collection_id = collection_id.strip()
        if not self._validate_collection_id(collection_id):
            raise FileLoadError("Collection ID is missing")
        self.collection_id = collection_id
        self.retrieve_collection_files()

    def retrieve_collection_files(self):
        logger = logging.getLogger("corpus-loader")
        if self.api_key is None:
            self.collection_files = []
            raise FileLoadError("No API key set")

        api_root: str = self._get_api_root()

        r = requests.get(
            api_root + "object/open",
            params={"id": self.collection_id, "noUrid": None, "resolve-parts": None},
        )

        logger.log(logging.DEBUG, f"Final URL: {r.url}")

        # Print the history of the request to see if there were any redirects
        for response in r.history:
            logger.log(logging.DEBUG, f"Redirected from: {response.url}")

        try:
            r.raise_for_status()
        except Exception as e:
            self.collection_files = []
            raise FileLoadError(str(e))

        metadata = r.json()
        if metadata.get('error') is not None:
            self.collection_files = []
            raise FileLoadError('Error retrieving collection. Ensure the collection ID is correct')
        metadata_items = metadata.get('@graph')
        if metadata_items is None:
            self.collection_files = []
            raise FileLoadError('No items found in collection')

        all_file_refs: list[FileReference] = []
        for item in metadata_items:
            item_type = item.get("@type")
            if "File" in item_type:
                filepath = item["@id"]

                file_refs: list[FileReference] = self.file_ref_factory.get_file_refs_from_path(filepath, False)
                all_file_refs.extend(file_refs)
            elif "Dataset" in item_type:
                dataset_parts = item["hasPart"]
                for dataset_item in dataset_parts:
                    filepath = dataset_item["@id"]

                    file_refs: list[FileReference] = self.file_ref_factory.get_file_refs_from_path(filepath, False)
                    all_file_refs.extend(file_refs)

        all_file_refs.sort(key=lambda ref: ref.get_path())

        self.collection_files = all_file_refs

    def get_all_files(self, expand_archived: bool) -> list[FileReference]:
        return self.collection_files

    def add_corpus_files(self, corpus_filepaths: list[str], include_hidden: bool, tqdm_obj: Tqdm):
        for filepath in tqdm_obj(corpus_filepaths, desc="Retrieving corpus files", unit="files", leave=False):
            file_ref: RemoteFileReference = self.file_ref_factory.get_oni_file_ref(filepath)
            if file_ref in self.loaded_corpus_files:
                continue
            if not include_hidden and file_ref.is_hidden():
                continue
            data = requests.get(file_ref.get_path(),
                                headers=self._get_auth_header()
                                )

            try:
                data.raise_for_status()
            except Exception as e:
                if str(e).startswith('404'):
                    continue
                elif str(e).startswith('401'):
                    raise FileLoadError(f"Denied permission to access file: {filepath}<br>Check API Key")
                else:
                    raise FileLoadError(f"Unexpected error loading file: {filepath}<br>{str(e)}")

            content_buf = BytesIO(data.text.encode('utf-8'))
            file_ref.set_content_buffer(content_buf)

            self.loaded_corpus_files.add(file_ref)

    def add_meta_files(self, meta_filepaths: list[str], include_hidden: bool, tqdm_obj: Tqdm):
        for filepath in tqdm_obj(meta_filepaths, desc="Retrieving metadata files", unit="files", leave=False):
            file_ref: RemoteFileReference = self.file_ref_factory.get_oni_file_ref(filepath)
            if file_ref in self.loaded_meta_files:
                continue
            if not include_hidden and file_ref.is_hidden():
                continue
            data = requests.get(file_ref.get_path(),
                                headers=self._get_auth_header()
                                )

            try:
                data.raise_for_status()
            except Exception as e:
                if str(e).startswith('404'):
                    continue
                elif str(e).startswith('401'):
                    raise FileLoadError(f"Denied permission to access file: {filepath}<br>Check API Key")
                else:
                    raise FileLoadError(f"Unexpected error loading file: {filepath}<br>{str(e)}")

            content_buf = BytesIO()
            content_buf.write(data.text.encode('utf-8'))
            file_ref.set_content_buffer(content_buf)

            self.loaded_meta_files.add(file_ref)

    def import_files_as_corpus(self, corpus_filepaths: list[str],
                               include_hidden: bool, tqdm_obj: Tqdm) -> list[DataFrameCorpus]:
        if len(self.loaded_corpus_files) or len(self.loaded_meta_files):
            raise FileLoadError("Can't import while files are loaded. Unload all files and then try importing again.")

        if len(corpus_filepaths) == 0:
            raise FileLoadError("No files selected for import.")

        corpus_ls: list[DataFrameCorpus] = []
        for filepath in tqdm_obj(corpus_filepaths, desc="Importing corpus files", unit="files", leave=False):
            file_ref: RemoteFileReference = self.file_ref_factory.get_oni_file_ref(filepath)
            if file_ref.get_extension().upper() != LoaderService.IMPORTABLE_FILETYPE:
                raise FileLoadError(f'Only {LoaderService.IMPORTABLE_FILETYPE} files can be imported.')
            if not include_hidden and file_ref.is_hidden():
                continue
            data = requests.get(file_ref.get_path(),
                                headers=self._get_auth_header()
                                )

            try:
                data.raise_for_status()
            except Exception as e:
                if str(e).startswith('404'):
                    continue
                elif str(e).startswith('401'):
                    raise FileLoadError(f"Denied permission to access file: {filepath}<br>Check API Key")
                else:
                    raise FileLoadError(f"Unexpected error loading file: {filepath}<br>{str(e)}")

            content_buf = BytesIO()
            content_buf.write(data.text.encode('utf-8'))
            content_buf.seek(0)
            try:
                corpus = DataFrameCorpus.deserialise(content_buf)
            except FileNotFoundError as e:
                raise FileLoadError(str(e))

            corpus_ls.append(corpus)

        return corpus_ls
