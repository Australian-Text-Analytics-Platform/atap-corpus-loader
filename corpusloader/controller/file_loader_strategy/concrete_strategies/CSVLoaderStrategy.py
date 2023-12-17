from io import StringIO

from pandas import DataFrame, read_csv

from corpusloader.controller.data_objects import CorpusHeader, DataType
from corpusloader.controller.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class CSVLoaderStrategy(FileLoaderStrategy):
    def get_inferred_headers(self) -> list[CorpusHeader]:
        df: DataFrame = read_csv(self.filepath, header=0, nrows=2)
        headers: list[CorpusHeader] = []
        for header_name, dtype_obj in df.dtypes.items():
            dtype_str: str = str(dtype_obj).upper()
            dtype: DataType
            try:
                dtype = DataType[dtype_str]
            except KeyError:
                dtype = DataType['STRING']
            headers.append(CorpusHeader(str(header_name), dtype, True))

        return headers

    def get_dataframe(self, headers: list[CorpusHeader]) -> DataFrame:
        df: DataFrame = read_csv(self.filepath, header=0)
        dtypes_applied_df: DataFrame = FileLoaderStrategy._apply_selected_headers(df, headers)

        return dtypes_applied_df
