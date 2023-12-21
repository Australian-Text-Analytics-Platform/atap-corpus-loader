from enum import Enum

from corpusloader.controller.data_objects import FileReference
from corpusloader.controller.file_loader_strategy.FileLoadError import FileLoadError
from corpusloader.controller.file_loader_strategy.concrete_strategies import *
from corpusloader.controller.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class FileType(Enum):
    """
    Maps file extensions to concrete FileLoaderStrategy types.
    The file extensions should be treated as case-insensitive
    """
    TXT = TXTLoaderStrategy
    ODT = ODTLoaderStrategy
    DOCX = DOCXLoaderStrategy
    CSV = CSVLoaderStrategy
    TSV = TSVLoaderStrategy
    XLSX = XLSXLoaderStrategy
    ODS = ODSLoaderStrategy
    RDS = RLoaderStrategy
    RDATA = RLoaderStrategy
    RDA = RLoaderStrategy


class FileLoaderFactory:
    """
    Provides a single public method to map a FileReference object to concrete FileLoaderStrategy object
    """
    @staticmethod
    def get_file_loader(file_ref: FileReference) -> FileLoaderStrategy:
        """
        Maps the provided FileReference object to a concrete FileLoaderStrategy object based on the extension.
        If the file extension is missing (the filename is not of the format <name>.<extension> or is not
        valid (i.e. is not a member of the FileType enum) a FileLoadError will be raised.
        :param file_ref: the FileReference object corresponding to the file to assign a loader to
        :return: a concrete FileLoaderStrategy object that has been passed the provided FileReference object.
        :raises FileLoadError: if there is no '.' in the file name or the extension after the '.' is not a valid file type
        """
        file_type: FileType = FileLoaderFactory._get_file_type(file_ref)
        file_loader: FileLoaderStrategy = file_type.value(file_ref)

        return file_loader

    @staticmethod
    def _get_file_type(file_ref: FileReference) -> FileType:
        file_name: str = file_ref.get_filename()
        if '.' not in file_name:
            raise FileLoadError(f"No file extension found in file name: {file_name}. "
                                f"File name must be in format <filename>.<extension>")
        extension: str = file_name.split('.')[-1]
        try:
            return FileType[extension.upper()]
        except KeyError:
            accepted_types: str = ', '.join([ft.name for ft in FileType])
            raise FileLoadError(f"Invalid file type loaded: {extension}. Valid file types: {accepted_types}")
