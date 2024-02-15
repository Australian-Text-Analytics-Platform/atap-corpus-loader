from os.path import join, relpath, dirname, basename
from tempfile import NamedTemporaryFile
from typing import Optional
from zipfile import ZipFile


class FileReference:
    """
    A general purpose object to hold information regarding a specific file in the file system.
    Folder structure is preserved as a path-like string
    """
    def __init__(self, path: str):
        """
        :param path: the path to the file. This can be absolute or relative to the root_directory specified in CorpusLoader
        """
        self.path: str = path
        self.directory_path: str = dirname(path)
        self.filename: str = basename(path)

        self.extension: str
        if '.' not in self.filename:
            self.extension = ''
        else:
            self.extension = self.filename.split('.')[-1]

    def __eq__(self, other):
        if not isinstance(other, FileReference):
            return False
        return self.get_path() == other.get_path()

    def __hash__(self):
        return hash(self.get_path())

    def __str__(self):
        return self.get_path()

    def __repr__(self):
        return self.get_path()

    def resolve_real_file_path(self) -> str:
        """
        Provides a real addressable path to the file contents. If the FileReference object is an instance of
        ZipFileReference, the file is extracted, placed in a temporary file, and the temporary file path will be provided
        :return: the full addressable path of the file
        """
        return self.get_path()

    def get_path(self) -> str:
        """
        :return: the path to the file
        """
        return self.path

    def get_directory_path(self) -> str:
        """
        :return: the path to the immediate parent directory of the file
        """
        return self.directory_path

    def get_filename(self) -> str:
        """
        :return: the filename of the file, including file extension
        """
        return self.filename

    def is_hidden(self) -> bool:
        """
        :return: True if the filename begins with a '.', False otherwise
        """
        return self.filename.startswith('.')

    def get_extension(self) -> str:
        """
        :return: the filetype extension of the file (case-sensitive), excluding the '.'.
        If the filename is 'example.txt', this method will return 'txt'.
        """
        return self.extension

    def is_zipped(self) -> bool:
        """
        If True, the file is contained within a zip archive. In this case, the path returned by get_full_path()
        is not a real addressable path, just a string representation of where the file is located. A real addressable
        path can be obtained from resolve_real_file_path()
        :return: True if FileReference object is an instance of ZipFileReference, False otherwise
        """
        return False


class ZipFileReference(FileReference):
    def __init__(self, zip_file_path: str, internal_path: str):
        """
        :param zip_file_path: the path to the zip file that holds this zipped file. This can be absolute or relative to the root_directory specified in CorpusLoader
        :param internal_path: the path within the zip file to this zipped file
        """
        self.path: str = join(zip_file_path, internal_path)
        self.directory_path: str = zip_file_path
        self.internal_directory: str = dirname(internal_path)
        self.filename: str = basename(internal_path)

        self.extension: str
        if '.' not in self.filename:
            self.extension = ''
        else:
            self.extension = self.filename.split('.')[-1]

        self.zip_file = None

    def get_path(self) -> str:
        """
        :return: the joined zip_file_path and internal_path to form the full path of the file
        """
        return self.path

    def is_zipped(self) -> bool:
        """
        If True, the file is contained within a zip archive. In this case, the path returned by get_full_path()
        is not a real addressable path, just a string representation of where the file is located. A real addressable
        path can be obtained from resolve_real_file_path()
        :return: True as FileReference object is an instance of ZipFileReference
        """
        return True

    def resolve_real_file_path(self) -> str:
        """
        Provides a real addressable path to the file contents. The zipped file is extracted,
        placed in a temporary file, and the temporary file path is provided
        :return: the full addressable path of the file
        """
        internal_path = join(self.internal_directory, self.filename)
        zip_file = ZipFile(self.directory_path)
        with zip_file.open(internal_path, force_zip64=True) as zip_f:
            file_content = zip_f.read()
        with NamedTemporaryFile(delete=False) as temp_f:
            temp_f.write(file_content)
            real_path = temp_f.name

        return real_path


class FileReferenceCache:
    """
    An add-only cache for FileReference objects. The cache maintains a dictionary which maps full_path strings
    to the corresponding FileReference object.
    The cache is intended to mitigate the overhead of re-creating FileReference objects, as the files within the file
    system are expected to change far less frequently than FileReference objects are referred to.
    """
    def __init__(self):
        self.file_ref_cache: dict[str, FileReference] = {}

    def clear_cache(self):
        """
        Resets the cache to an empty dictionary
        """
        self.file_ref_cache = {}

    def get_file_ref(self, path: str) -> FileReference:
        cached_ref: Optional[FileReference] = self.file_ref_cache.get(path)
        if cached_ref is None:
            cached_ref = FileReference(path)
            self.file_ref_cache[path] = cached_ref

        return cached_ref

    def get_zip_file_refs(self, zip_file_path: str) -> list[FileReference]:
        """
        Accepts a zip file and provides a list of FileReference
        objects that correspond to the zipped files within the zip archive.
        :param zip_file_path: the path to the zip archive that holds the files to be listed.
        :return: a list of FileReference objects corresponding to the files within the zip archive
        """
        with ZipFile(zip_file_path) as zip_f:
            info_list = zip_f.infolist()

        file_refs: list[FileReference] = []
        for info in info_list:
            if info.is_dir():
                continue
            zip_ref: FileReference = self._get_single_zip_file_ref(zip_file_path, info.filename)
            file_refs.append(zip_ref)

        return file_refs

    def _get_single_zip_file_ref(self, zip_file_path: str, internal_path: str) -> ZipFileReference:
        full_path: str = join(zip_file_path, internal_path)
        cached_ref: Optional[ZipFileReference] = self.file_ref_cache.get(full_path)
        if cached_ref is None:
            cached_ref = ZipFileReference(zip_file_path, internal_path)
            self.file_ref_cache[full_path] = cached_ref

        return cached_ref
