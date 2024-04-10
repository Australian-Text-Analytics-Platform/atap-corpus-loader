from os.path import join, basename
from tempfile import TemporaryDirectory
from typing import Optional

import requests
from rocrate.rocrate import ROCrate


class OniAPIError(Exception):
    pass


class OniAPIService:
    def __init__(self):
        self.providers: dict[str, str] = {
            "ATAP": "https://data.atap.edu.au",
            "LDaCA": "https://data.ldaca.edu.au"
        }
        self.curr_provider: str = "ATAP"
        self.access_token: Optional[str] = "eyJhbGciOiJIUzI1NiJ9.eyJpZCI6ImZlYzVlODA3LTQ3MDgtNDY0NS04ODY5LTI1OGI5MzJhYjRiYSIsImVtYWlsIjoiaGFtaXNoLmNyb3NlckBzeWRuZXkuZWR1LmF1IiwibmFtZSI6IkhhbWlzaCBDcm9zZXIiLCJhZG1pbmlzdHJhdG9yIjpmYWxzZSwidXBsb2FkIjpmYWxzZSwiZXhwaXJlcyI6IjIwMjQtMDQtMDhUMTE6NDc6NDguMjQ3WiJ9.i5vu5_Chab2zZ7nin95YwUevxrZANsgEwc3LQosbGwc"

    def _get_base_url(self) -> str:
        base_url: Optional[str] = self.providers.get(self.curr_provider)
        return base_url if base_url else ''

    def _get_auth_header(self) -> dict:
        return {'Authori': self.access_token}

    def _validate_collection_id(self, collection_id) -> bool:
        if len(collection_id) == 0:
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

    def get_auth_url(self) -> str:
        # url: str = f"{self._get_base_url()}/api/oauth/cilogon/login"
        # r = requests.get(url)
        # auth_url = r.json().get('url')
        # return auth_url
        return f"{self._get_base_url()}/api/user/token"

    def set_access_token(self, api_key: str):
        self.access_token = api_key

    # Mike code

    def _load_collection(self, crate_dir: str, collection_id: str) -> ROCrate:
        url = f"{self._get_base_url()}/api/object/meta?resolve-parts&id={collection_id}"
        r = requests.get(url)
        if r.status_code != 200:
            raise OniAPIError(f"Error fetching collection metadata for '{url}'")

        rcj = r.json()
        if "error" in rcj:
            raise OniAPIError(f"Error fetching collection metadata for '{url}'")
        ro_metadata = join(crate_dir, "ro-crate-metadata.json")
        with open(ro_metadata, "w") as rmf:
            rmf.write(r.text)
        return ROCrate(crate_dir)

    def _download_part(self, crate_dir: str, part) -> str:
        """Download one bytestream"""
        # auth_header = self._get_auth_header()
        url_with_auth = f"{part.id}&oni-user-token={self.access_token}"
        r = requests.get(url_with_auth)
        if r.status_code != 200:
            raise OniAPIError(f"Error {r.status_code} fetching collection part '{part.id}'")
        filename: str = basename(part.id)
        filepath: str = join(crate_dir, filename)
        with open(filepath, 'wb') as part_f:
            part_f.write(r.content)

        return filepath

    def _get_root(self, crate: ROCrate):
        metadata_descriptor = crate.dereference("ro-crate-metadata.json")
        root_id = metadata_descriptor["about"]
        root_entity = crate.dereference(root_id["@id"])
        return root_entity

    def retrieve_collection(self, collection_id: str) -> list[str]:
        if not self._validate_collection_id(collection_id):
            raise OniAPIError(f"Collection ID {collection_id} is not valid")

        temp_dir = TemporaryDirectory()
        crate: ROCrate = self._load_collection(temp_dir.name, collection_id)
        root = self._get_root(crate)
        corpus_files: list[str] = []
        for part in root["hasPart"]:
            if ("File" in part.type) and ("txt" in part.id):
                filepath = self._download_part(temp_dir.name, part)
                corpus_files.append(filepath)
        return corpus_files
