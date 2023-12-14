from os.path import basename

from odf import text, teletype
from odf.opendocument import load
from pandas import DataFrame

from corpusloader.controller.data_objects import CorpusHeader, DataType
from corpusloader.controller.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class ODTLoaderStrategy(FileLoaderStrategy):
    def get_inferred_headers(self) -> list[CorpusHeader]:
        headers: list[CorpusHeader] = [
            CorpusHeader("document", DataType.STRING, True),
            CorpusHeader("filename", DataType.STRING, True),
            CorpusHeader("directory", DataType.CATEGORY, True)
        ]

        return headers

    def get_dataframe(self) -> DataFrame:
        odt_doc = load(self.filepath)
        document = ''
        for element in odt_doc.getElementsByType(text.P):
            document += teletype.extractText(element)

        file_name = basename(self.filepath)
        file_data = {"document": document, "filename": file_name, "directory": self.filepath}

        return DataFrame(file_data)
