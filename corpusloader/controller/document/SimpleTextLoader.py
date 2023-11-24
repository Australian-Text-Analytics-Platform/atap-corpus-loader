import os
from io import BytesIO
from pathlib import Path

from atap_corpus.corpus.corpus import DataFrameCorpus
from pandas import DataFrame

from corpusloader.controller.document.DocumentLoader import DocumentLoader
from corpusloader.controller.document.FileLoadError import FileLoadError


class SimpleTextLoader(DocumentLoader):
    USER_FRIENDLY_NAME: str = "Simple Text Collection"
    DATA_DESCRIPTION: str = "One or more text files encoded in UTF-8 with no metadata"

    @staticmethod
    def get_user_friendly_name():
        return SimpleTextLoader.USER_FRIENDLY_NAME

    @staticmethod
    def get_data_description():
        return SimpleTextLoader.DATA_DESCRIPTION

    @staticmethod
    def load_corpus_from_bytes(content_ls: list[BytesIO], content_names: list[str]) -> DataFrameCorpus:
        raise NotImplementedError()

    @staticmethod
    def load_corpus_from_filepath(filepath_ls: list[Path]) -> DataFrameCorpus:
        document_col_name: str = "text"
        documents: list[dict] = []
        for filepath in filepath_ls:
            with open(filepath) as f:
                file_str: str = f.read()
                filename: str = os.path.basename(filepath)
            document_data = {document_col_name: file_str, "text_id": filename}
            documents.append(document_data)

        document_df: DataFrame = DataFrame(documents)
        return DataFrameCorpus.from_dataframe(document_df, col_doc=document_col_name)
