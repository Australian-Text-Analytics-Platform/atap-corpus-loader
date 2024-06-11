from io import BytesIO

from pandas import DataFrame, read_csv

from atap_corpus_loader.controller.data_objects import CorpusHeader, DataType
from atap_corpus_loader.controller.loader_service.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class CSVLoaderStrategy(FileLoaderStrategy):
    @staticmethod
    def _rename_headers(df: DataFrame):
        df.columns = [f'Data_{c}' for c in df.columns.astype(str)]

    @staticmethod
    def _detect_headers(file_buf: BytesIO) -> bool:
        read_rows = 10
        file_buf.seek(0)
        df_no_header = read_csv(file_buf, header=None, nrows=read_rows)
        file_buf.seek(0)
        df_header = read_csv(file_buf, nrows=read_rows)
        file_buf.seek(0)
        return tuple(df_no_header.dtypes) != tuple(df_header.dtypes)

    def get_inferred_headers(self) -> list[CorpusHeader]:
        read_rows = 10
        file_buf: BytesIO = self.file_ref.get_content_buffer()
        contains_header_row: bool = self._detect_headers(file_buf)
        if contains_header_row:
            df = read_csv(file_buf, nrows=read_rows)
        else:
            df = read_csv(file_buf, header=None, nrows=read_rows)
            self._rename_headers(df)
        headers: list[CorpusHeader] = []
        for header_name, dtype_obj in df.dtypes.items():
            dtype: DataType
            try:
                dtype = DataType(str(dtype_obj))
            except ValueError:
                dtype = DataType.TEXT
            headers.append(CorpusHeader(str(header_name), dtype))

        return headers

    def get_dataframe(self, headers: list[CorpusHeader]) -> DataFrame:
        file_buf: BytesIO = self.file_ref.get_content_buffer()
        included_headers: list[str] = [header.name for header in headers if header.include]
        if self._detect_headers(file_buf):
            df = read_csv(file_buf, header=0, dtype=object, usecols=included_headers)
        else:
            df = read_csv(file_buf, header=None, dtype=object)
            self._rename_headers(df)
            df = df[included_headers]
        dtypes_applied_df: DataFrame = FileLoaderStrategy._apply_selected_dtypes(df, headers)

        return dtypes_applied_df
