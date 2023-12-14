from enum import Enum
from os.path import basename

from corpusloader.controller.file_loader_strategy.FileLoadError import FileLoadError
from corpusloader.controller.file_loader_strategy.concrete_strategies import *
from corpusloader.controller.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class FileType(Enum):
    TXT = TXTLoaderStrategy
    ODT = ODTLoaderStrategy
    DOCX = DOCXLoaderStrategy
    CSV = CSVLoaderStrategy
    TSV = TSVLoaderStrategy
    XLSX = XLSXLoaderStrategy
    ODS = ODSLoaderStrategy
    RDS = RDSLoaderStrategy


class FileLoaderFactory:
    @staticmethod
    def get_file_loader(filepath: str) -> FileLoaderStrategy:
        file_type: FileType = FileLoaderFactory._get_file_type(filepath)
        file_loader: FileLoaderStrategy = file_type.value(filepath)

        return file_loader

    @staticmethod
    def _get_file_type(filepath: str) -> FileType:
        file_name: str = basename(filepath)
        if '.' not in file_name:
            raise FileLoadError(f"No file extension found in file name: {filepath}. "
                                f"File name must be in format <filename>.<extension>")
        extension: str = file_name.split('.')[-1]
        try:
            return FileType[extension.upper()]
        except KeyError:
            accepted_types: str = ', '.join([ft.name for ft in FileType])
            raise FileLoadError(f"Invalid file type loaded: {extension}. Valid file types: {accepted_types}")
