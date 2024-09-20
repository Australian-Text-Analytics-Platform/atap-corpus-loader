from abc import ABC, abstractmethod

from pandas import DataFrame, to_datetime

from atap_corpus_loader.controller.data_objects import CorpusHeader, FileReference, DataType, HeaderStrategy
from atap_corpus_loader.controller.loader_service.FileLoadError import FileLoadError


class FileLoaderStrategy(ABC):
    """
    An abstract class for loading files as DataFrame objects to be used in a DataFrameCorpus.
    A concrete class should extend this class for each file type that is supported.
    """
    def __init__(self, file_ref: FileReference):
        """
        :param file_ref: the FileReference object corresponding to the file to be loaded
        """
        self.file_ref: FileReference = file_ref

    @staticmethod
    def _apply_selected_dtypes(df: DataFrame, headers: list[CorpusHeader]) -> DataFrame:
        """
        Attempts to cast each column within the provided DataFrame to the data types specified in headers.
        :param df: the DataFrame object whose columns will be type cast
        :param headers: the CorpusHeader objects representing the columns of the DataFrame. CorpusHeader objects with
        include as False will be ignored.
        :return: the DataFrame with columns cast to the given data types
        """

        for header in headers:
            if not header.include:
                continue
            if header.datatype == DataType.DATETIME:
                # Datetimes require handling timezone aware and timezone naive cases
                col = to_datetime(df[header.name], errors='coerce')
                if col.dt.tz is not None:
                    col = col.dt.tz_convert(None)
                df[header.name] = col
            else:
                try:
                    df[header.name] = df[header.name].astype(header.datatype.value)
                except ValueError:
                    raise FileLoadError(f"Could not cast value from {header.name} to {header.datatype.name}. Try modifying the selected datatype")

        return df

    @abstractmethod
    def get_inferred_headers(self, header_strategy: HeaderStrategy) -> list[CorpusHeader]:
        """
        Provides a list of CorpusHeader objects corresponding to the data found within the file.
        Some additional metadata headers may be provided not found within the file, such as filepath
        :param header_strategy: the method by which reading headers from tabular data will be handled
        :type header_strategy: HeaderStrategy
        :return: a list of CorpusHeader objects corresponding to the data found within the file
        :rtype: list[CorpusHeader]
        """
        raise NotImplementedError()

    @abstractmethod
    def get_dataframe(self, headers: list[CorpusHeader], header_strategy: HeaderStrategy) -> DataFrame:
        """
        Provides a DataFrame object containing the data from the loaded file.
        Columns of the DataFrame will be cast to the data types specified in the headers parameter.
        The DataFrame will exclude a column of data if its corresponding CorpusHeader object has include set to False
        :param headers: a list of CorpusHeader objects corresponding to the data found within the file
        :type headers: list[CorpusHeader]
        :param header_strategy: the method by which reading headers from tabular data will be handled
        :type header_strategy: HeaderStrategy
        :return: a DataFrame object corresponding to the loaded file and its provided CorpusHeader list
        :rtype: DataFrame
        """
        raise NotImplementedError()

