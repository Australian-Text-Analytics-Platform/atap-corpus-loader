from corpusloader.controller.document.DocumentLoader import DocumentLoader
from corpusloader.controller.document.FileLoadError import FileLoadError


class CSVLoader(DocumentLoader):
    USER_FRIENDLY_NAME: str = "CSV Collection"
    DATA_DESCRIPTION: str = """One or more CSV files encoded in UTF-8 with or without metadata.
    The column representing the documents must be named 'text'.
    If more than one CSV file is loaded, each file must have the same column headers, i.e. the same metadata"""

    @staticmethod
    def get_user_friendly_name():
        return CSVLoader.USER_FRIENDLY_NAME

    @staticmethod
    def get_data_description():
        return CSVLoader.DATA_DESCRIPTION

    @staticmethod
    def load_corpus_from_bytes(content: bytes, content_name: str):
        raise NotImplementedError()

    @staticmethod
    def load_corpus_from_filepath(filepath: str):
        raise NotImplementedError()
