from os.path import basename

from pandas import DataFrame

from corpusloader.controller.data_objects import CorpusHeader, DataType
from corpusloader.controller.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class TXTLoaderStrategy(FileLoaderStrategy):
    def get_inferred_headers(self) -> list[CorpusHeader]:
        headers: list[CorpusHeader] = [
            CorpusHeader('document', DataType.STRING, True),
            CorpusHeader('filename', DataType.STRING, True),
            CorpusHeader('filepath', DataType.CATEGORY, True)
        ]

        return headers

    def get_dataframe(self, headers: list[CorpusHeader]) -> DataFrame:
        with open(self.filepath) as f:
            document = f.read()
        file_name = basename(self.filepath)

        included_headers: list[str] = [header.name for header in headers if header.include]
        file_data = {}
        if 'document' in included_headers:
            file_data['document'] = [document]
        if 'filename' in included_headers:
            file_data['filename'] = [file_name]
        if 'filepath' in included_headers:
            file_data['filepath'] = [self.filepath]

        df: DataFrame = DataFrame(file_data)
        dtypes_applied_df: DataFrame = FileLoaderStrategy._apply_selected_dtypes(df, headers)

        return dtypes_applied_df
