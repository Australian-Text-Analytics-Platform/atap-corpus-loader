from io import BytesIO
from xml.etree.ElementTree import parse, Element

from pandas import DataFrame

from atap_corpus_loader.controller.data_objects import CorpusHeader, DataType, HeaderStrategy
from atap_corpus_loader.controller.loader_service.file_loader_strategy import FileLoaderStrategy


class XMLLoaderStrategy(FileLoaderStrategy):
    def _extract_text(self, element: Element) -> str:
        text = element.text or ''
        for child in element:
            text += self._extract_text(child)
            if child.tail:
                text += child.tail

        return text

    def get_inferred_headers(self, header_strategy: HeaderStrategy) -> list[CorpusHeader]:
        headers: list[CorpusHeader] = [
            CorpusHeader('document', DataType.TEXT, include=True),
            CorpusHeader('filename', DataType.TEXT),
            CorpusHeader('filepath', DataType.TEXT)
        ]

        return headers

    def get_dataframe(self, headers: list[CorpusHeader], header_strategy: HeaderStrategy) -> DataFrame:
        included_headers: list[str] = [header.name for header in headers if header.include]
        file_data = {}
        if 'document' in included_headers:
            file_buf: BytesIO = self.file_ref.get_content_buffer()
            raw_xml_tree = parse(file_buf)
            root = raw_xml_tree.getroot()
            document = self._extract_text(root)

            file_data['document'] = [document]
        if 'filename' in included_headers:
            file_data['filename'] = [self.file_ref.get_filename_no_ext()]
        if 'filepath' in included_headers:
            file_data['filepath'] = [self.file_ref.get_path()]

        df: DataFrame = DataFrame(file_data, dtype='string')

        return df
