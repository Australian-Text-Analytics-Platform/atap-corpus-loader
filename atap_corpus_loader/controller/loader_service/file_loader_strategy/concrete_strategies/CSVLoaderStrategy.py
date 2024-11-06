from io import BytesIO
from typing import Optional

from pandas import DataFrame, read_csv, to_datetime, Series, concat
from panel.widgets import Tqdm

from atap_corpus_loader.controller.data_objects import CorpusHeader, DataType, HeaderStrategy
from atap_corpus_loader.controller.loader_service.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class CSVLoaderStrategy(FileLoaderStrategy):
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
        df_no_header = read_csv(file_buf, header=None, nrows=read_rows)
        file_buf.seek(0)
        df_header = read_csv(file_buf, nrows=read_rows)
        file_buf.seek(0)
        return tuple(df_no_header.dtypes) != tuple(df_header.dtypes)

    def get_inferred_headers(self, header_strategy: HeaderStrategy) -> list[CorpusHeader]:
        read_rows = 10
        file_buf: BytesIO = self.file_ref.get_content_buffer()
        header_detected: bool = self._detect_headers(file_buf)
        if (header_strategy == header_strategy.HEADERS) or ((header_strategy == header_strategy.INFER) and header_detected):
            df = read_csv(file_buf, nrows=read_rows)
        else:
            df = read_csv(file_buf, header=None, nrows=read_rows)
            self._rename_headers(df)
        headers: list[CorpusHeader] = []
        empty_columns = df.columns[df.isna().all()]
        df[empty_columns] = df[empty_columns].astype('string')
        for header_name, dtype_obj in df.dtypes.items():
            if self.is_datetime_castable(df[header_name]):
                headers.append(CorpusHeader(str(header_name), DataType.DATETIME))
                continue

            try:
                dtype = DataType(str(dtype_obj))
            except ValueError:
                dtype = DataType.TEXT
            headers.append(CorpusHeader(str(header_name), dtype))

        return headers

    def get_dataframe(self, headers: list[CorpusHeader], header_strategy: HeaderStrategy, tqdm_obj: Optional[Tqdm] = None) -> DataFrame:
        file_buf: BytesIO = self.file_ref.get_content_buffer()
        included_headers: list[str] = [header.name for header in headers if header.include]
        header_detected: bool = self._detect_headers(file_buf)

        chunksize = 10000
        total_lines = sum(1 for _ in file_buf)
        file_buf.seek(0)

        if (header_strategy == header_strategy.HEADERS) or ((header_strategy == header_strategy.INFER) and header_detected):
            df = concat(tqdm_obj(read_csv(file_buf, chunksize=chunksize, header=0, dtype=object, usecols=included_headers), total=((total_lines-1) // chunksize)+1, unit="chunks", desc="Reading CSV"))
        else:
            df = concat(tqdm_obj(read_csv(file_buf, chunksize=chunksize, header=None, dtype=object), total=(total_lines // chunksize)+1, unit="chunks", desc="Reading CSV"))
            self._rename_headers(df)
            df = df[included_headers]

        dtypes_applied_df: DataFrame = FileLoaderStrategy._apply_selected_dtypes(df, headers)

        return dtypes_applied_df
