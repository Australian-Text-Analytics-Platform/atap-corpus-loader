from os.path import basename

from docx import Document
from pandas import DataFrame

from corpusloader.controller.data_objects import CorpusHeader, DataType
from corpusloader.controller.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class DOCXLoaderStrategy(FileLoaderStrategy):
    def get_inferred_headers(self) -> list[CorpusHeader]:
        headers: list[CorpusHeader] = [
            CorpusHeader("document", DataType.STRING, True),
            CorpusHeader("filename", DataType.STRING, True),
            CorpusHeader("directory", DataType.CATEGORY, True)
        ]

        return headers

    def get_dataframe(self, headers: list[CorpusHeader]) -> DataFrame:
        docx_doc = Document(self.filepath)
        document = ''
        for paragraph in docx_doc.paragraphs:
            document += paragraph.text + '\n'

        file_name = basename(self.filepath)
        file_data = {"document": [document], "filename": [file_name], "directory": [self.filepath]}

        return DataFrame(file_data)
