from io import BytesIO
from typing import Optional

from pandas import DataFrame
from panel.widgets import Tqdm

from atap_corpus_loader.controller.data_objects import CorpusHeader, DataType, HeaderStrategy
from atap_corpus_loader.controller.loader_service.file_loader_strategy import FileLoaderStrategy


class XMLLoaderStrategy(FileLoaderStrategy):
    def get_inferred_headers(self, header_strategy: HeaderStrategy) -> list[CorpusHeader]:
        headers: list[CorpusHeader] = [
            CorpusHeader('document', DataType.TEXT, include=True),
            CorpusHeader('filename', DataType.TEXT),
            CorpusHeader('filepath', DataType.TEXT)
        ]

        return headers

    def get_dataframe(self, headers: list[CorpusHeader], header_strategy: HeaderStrategy, tqdm_obj: Optional[Tqdm] = None) -> DataFrame:
        included_headers: list[str] = [header.name for header in headers if header.include]
        file_data = {}
        if 'document' in included_headers:
            file_buf: BytesIO = self.file_ref.get_content_buffer()
            document = file_buf.read()
            file_data['document'] = [document]
        if 'filename' in included_headers:
            file_data['filename'] = [self.file_ref.get_filename_no_ext()]
        if 'filepath' in included_headers:
            file_data['filepath'] = [self.file_ref.get_path()]

        df: DataFrame = DataFrame(file_data, dtype='string')

        return df
