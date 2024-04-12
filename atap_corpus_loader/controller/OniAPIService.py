from os.path import basename
from typing import Optional

import requests
from atap_corpus.corpus.corpus import DataFrameCorpus
from pandas import DataFrame
from panel.widgets import Tqdm


class OniAPIError(Exception):
    pass


class OniAPIService:
    def __init__(self):
        self.providers: dict[str, str] = {
            "ATAP": "https://data.atap.edu.au",
            "LDaCA": "https://data.ldaca.edu.au"
        }
        self.curr_provider: str = "ATAP"
        self.api_key: Optional[str] = None

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

    def set_api_key(self, api_key: str) -> bool:
        if self._validate_api_key(api_key):
            self.api_key = api_key
            return True
        return False

    def build_corpus(self, collection_id: str, tqdm_obj: Tqdm) -> DataFrameCorpus:
        if self.api_key is None:
            raise OniAPIError("No API key set")
        if not self._validate_collection_id(collection_id):
            raise OniAPIError(f"Collection ID {collection_id} is not valid")

        api_root: str = self._get_api_root()

        r = requests.get(
            api_root + "object/meta",
            params={"id": collection_id, "noUrid": "1"},
        )

        try:
            r.raise_for_status()
        except Exception as e:
            raise OniAPIError(str(e))

        corpus: dict[str, list] = {'text': [], 'filename': [], 'filepath': []}

        metadata = r.json()
        for item in tqdm_obj(metadata["@graph"], desc="Downloading corpus files", unit="files", leave=False):
            if item["@type"] == "RepositoryObject":
                # Use the indexable text part of the object - the other file
                # (part) included is the same but with the metadata embedded in the
                # document.
                text_object_path = item["indexableText"]["@id"]

                data = requests.get(
                    api_root + "stream",
                    params={
                        "id": collection_id,
                        "path": text_object_path,
                    },
                    headers=self._get_auth_header()
                )

                try:
                    data.raise_for_status()
                except Exception as e:
                    if str(e).startswith('401'):
                        raise OniAPIError(str(e))
                    continue

                corpus['text'].append(data.text)
                corpus['filepath'].append(text_object_path)
                corpus['filename'].append(basename(text_object_path))

        corpus_df: DataFrame = DataFrame(corpus, dtype=str)
        return DataFrameCorpus.from_dataframe(corpus_df, 'text', collection_id)
