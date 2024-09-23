from io import BytesIO

from pandas import DataFrame, read_excel, Series, to_datetime

from atap_corpus_loader.controller.data_objects import CorpusHeader, DataType, HeaderStrategy
from atap_corpus_loader.controller.loader_service.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class XLSXLoaderStrategy(FileLoaderStrategy):
    @staticmethod
    def is_datetime_castable(data_series: Series):
        if data_series.dtype != "object":
            return False
        try:
            to_datetime(data_series, format='mixed')
        except (ValueError, TypeError):
            return False
        return True

    @staticmethod
    def _rename_headers(df: DataFrame):
        df.columns = [f'Data_{c}' for c in df.columns.astype(str)]

    @staticmethod
    def _detect_headers(file_buf: BytesIO) -> bool:
        read_rows = 10
        file_buf.seek(0)
        df_no_header = read_excel(file_buf, header=None, nrows=read_rows)
        file_buf.seek(0)
        df_header = read_excel(file_buf, nrows=read_rows)
        file_buf.seek(0)
        return tuple(df_no_header.dtypes) != tuple(df_header.dtypes)

    def get_inferred_headers(self, header_strategy: HeaderStrategy) -> list[CorpusHeader]:
        read_rows = 10
        file_buf: BytesIO = self.file_ref.get_content_buffer()
        header_detected: bool = self._detect_headers(file_buf)
        if (header_strategy == header_strategy.HEADERS) or ((header_strategy == header_strategy.INFER) and header_detected):
            df = read_excel(file_buf, header=0, nrows=read_rows)
        else:
            df = read_excel(file_buf, header=None, nrows=read_rows)
            self._rename_headers(df)
        headers: list[CorpusHeader] = []
        empty_columns = df.columns[df.isna().all()]
        df[empty_columns] = df[empty_columns].astype('string')
        for header_name, dtype_obj in df.dtypes.items():
            dtype: DataType
            try:
                dtype = DataType(str(dtype_obj))
            except ValueError:
                dtype = DataType.TEXT
            headers.append(CorpusHeader(str(header_name), dtype))

        return headers

    def get_dataframe(self, headers: list[CorpusHeader], header_strategy: HeaderStrategy) -> DataFrame:
        file_buf: BytesIO = self.file_ref.get_content_buffer()
        included_headers: list[str] = [header.name for header in headers if header.include]
        header_detected: bool = self._detect_headers(file_buf)
        if (header_strategy == header_strategy.HEADERS) or ((header_strategy == header_strategy.INFER) and header_detected):
            df = read_excel(file_buf, header=0, dtype=object, usecols=included_headers)
        else:
            df = read_excel(file_buf, header=None, dtype=object)
            self._rename_headers(df)
            df = df[included_headers]
        dtypes_applied_df: DataFrame = FileLoaderStrategy._apply_selected_dtypes(df, headers)

        return dtypes_applied_df
