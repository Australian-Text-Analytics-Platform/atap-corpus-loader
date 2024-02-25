from io import BytesIO

from docx import Document
from pandas import DataFrame

from atap_corpus_loader.controller.data_objects import CorpusHeader, DataType, FileReference
from atap_corpus_loader.controller.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class DOCXLoaderStrategy(FileLoaderStrategy):
    def get_inferred_headers(self) -> list[CorpusHeader]:
        headers: list[CorpusHeader] = [
            CorpusHeader('document', DataType.TEXT, True),
            CorpusHeader('filename', DataType.TEXT, True),
            CorpusHeader('filepath', DataType.TEXT, True)
        ]

        return headers

    def get_dataframe(self, headers: list[CorpusHeader]) -> DataFrame:
        file_buf: BytesIO = self.file_ref.get_content_buffer()
        docx_doc = Document(file_buf)
        document = ''.join([p.text for p in docx_doc.paragraphs])

        included_headers: list[str] = [header.name for header in headers if header.include]
        file_data = {}
        if 'document' in included_headers:
            file_data['document'] = [document]
        if 'filename' in included_headers:
            file_data['filename'] = [self.file_ref.get_filename()]
        if 'filepath' in included_headers:
            file_data['filepath'] = [self.file_ref.get_path()]

        df: DataFrame = DataFrame(file_data, dtype='string')

        return df
