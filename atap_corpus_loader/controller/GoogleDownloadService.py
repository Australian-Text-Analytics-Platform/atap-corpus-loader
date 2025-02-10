from concurrent.futures import ThreadPoolExecutor
from os.path import normpath, sep
from re import Pattern, compile, search

import gdown
from gdown.exceptions import FileURLRetrievalError, FolderContentsMaximumLimitError


class GoogleDownloadService:
    """
    A GoogleDownloadService object provides methods for downloading publicly shared files from Google Drive using the gdown library.
    The files will be written to the directory specified in the constructor.
    """
    URL_PATTERN: Pattern = compile("https://drive.google.com/")

    def __init__(self, download_directory: str):
        """
        :param download_directory: The directory that the downloaded files will be written to
        :type download_directory: str
        """
        self.download_directory: str = self._sanitise_dir(download_directory)

    @staticmethod
    def _sanitise_dir(directory: str) -> str:
        if not isinstance(directory, str):
            raise TypeError(f"Expected directory to be str, got {type(directory)}")
        sanitised_directory = normpath(directory)

        if not sanitised_directory.endswith(sep):
            sanitised_directory += sep

        return str(sanitised_directory)

    @staticmethod
    def is_gdrive_url(gdrive_url: str) -> bool:
        match = search(GoogleDownloadService.URL_PATTERN, gdrive_url)
        return bool(match is not None)

    def _download_gdrive_file(self, gdrive_url: str):
        gdown.download(url=gdrive_url, output=self.download_directory, fuzzy=True)

    def download_files(self, gdrive_url: str):
        """
        Downloads the Google Drive object specified in the argument.
        A Thread Pool is used to ensure the (usually slow) download is not blocking for the calling code.
        The method will raise a ValueError if the gdown download function raises a specific error.
        :param gdrive_url: The publically sharable URL of the Google Drive object to be downloaded.
        :type gdrive_url: str
        """
        with ThreadPoolExecutor() as executor:
            future = executor.submit(self._download_gdrive_file, gdrive_url)
            try:
                future.result()
            except FileURLRetrievalError:
                raise ValueError("Failed to retrieve file url: Cannot retrieve the public link of the file.\nYou may need to change the permission to 'Anyone with the link', or have had many accesses.")
            except FolderContentsMaximumLimitError as e:
                raise ValueError(str(e))
