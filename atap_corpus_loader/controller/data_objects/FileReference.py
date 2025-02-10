from abc import ABC, abstractmethod
from io import BytesIO
from os.path import join, dirname, basename
from typing import Optional
from zipfile import ZipFile, BadZipFile


class FileReference(ABC):
    """
    FileReference is an abstract class that provides methods for retrieving information about a file.
    A pathlib implementation would be insufficient due to application-specific attributes/methods, especially with subclasses of FileReference.
    """
    def __init__(self, path: str):
        self.path: str = path
        self.path_hash: int = hash(self.path)
        self.directory_path: str = dirname(path)
        self.filename: str = basename(path)

        self.filename_no_ext: str
        self.extension: str
        if '.' not in self.filename:
            self.extension = ''
            self.filename_no_ext = self.filename
        else:
            filename_dot_split = self.filename.split('.')
            self.extension = filename_dot_split[-1]
            self.filename_no_ext = '.'.join(filename_dot_split[:-1])

        self.is_ref_archive = self.extension.lower() == 'zip'

    @abstractmethod
    def get_content_buffer(self) -> BytesIO:
        """
        Provides a BytesIO object which contains the contents of the file.
        :return: The BytesIO object containing the file contents
        :rtype: BytesIO
        """
        raise NotImplementedError()

    def __eq__(self, other):
        if not isinstance(other, FileReference):
            return False
        return self.path_hash == other.path_hash

    def __hash__(self):
        return self.path_hash

    def __str__(self):
        return self.get_path()

    def __repr__(self):
        return self.get_path()

    def get_path(self) -> str:
        """
        :return: the path to the file
        :rtype: str
        """
        return self.path

    def get_directory_path(self) -> str:
        """
        :return: the path to the immediate parent directory of the file
        :rtype: str
        """
        return self.directory_path

    def get_filename(self) -> str:
        """
        :return: the filename of the file, including file extension
        :rtype: str
        """
        return self.filename

    def get_filename_no_ext(self) -> str:
        """
        :return: the filename of the file, excluding file extension
        :rtype: str
        """
        return self.filename_no_ext

    def is_hidden(self) -> bool:
        """
        :return: True if the filename begins with a '.', False otherwise
        :rtype: bool
        """
        return self.filename.startswith('.')

    def get_extension(self) -> str:
        """
        :return: the filetype extension of the file (case-sensitive), excluding the '.'.
        If the filename is 'example.txt', this method will return 'txt'.
        :rtype: str
        """
        return self.extension

    def is_archive(self) -> bool:
        """
        Returns True if the file is an archive file (e.g. example.zip), False otherwise.
        Returns False for files within an archive (e.g. example.zip/text.txt)
        :return: True if the file is an archive file (e.g. example.zip), False otherwise.
        :rtype: bool
        """
        return self.is_ref_archive

    @staticmethod
    def is_zipped() -> bool:
        """
        Returns True if the file is within an archive (e.g. example.zip/text.txt), False otherwise.
        Returns False if file is an archive (e.g. example.zip)
        :return: True if the file is within an archive (e.g. example.zip/text.txt), False otherwise.
        :rtype: bool
        """
        return False


class DiskFileReference(FileReference):
    """
    A general purpose object to hold information regarding a specific file in the file system.
    Folder structure is preserved as a path-like string
    """
    def get_content_buffer(self) -> BytesIO:
        """
        Provides a BytesIO object which contains the contents of the file.
        :return: The BytesIO object containing the file contents
        :rtype: BytesIO
        """
        with open(self.get_path(), 'rb') as bytes_f:
            buf = BytesIO(bytes_f.read())
        return buf


class ZipFileReference(FileReference):
    """
    ZipFileReference refers to a zip file and provides an implementation of get_content_buffer that accounts for the zip format
    """
    def __init__(self, zip_file: ZipFile, zip_file_path: str, internal_path: str):
        """
        :param zip_file: the ZipFile object corresponding to the zip file that holds this zipped file. This allows multiple zipped files to share the same ZipFile object
        :param zip_file_path: the path to the zip file that holds this zipped file. This can be absolute or relative to the root_directory specified in CorpusLoader
        :param internal_path: the path within the zip file to this zipped file
        """
        super().__init__(join(zip_file_path, internal_path))
        self.zip_file = zip_file
        self.directory_path: str = zip_file_path
        self.internal_directory: str = dirname(internal_path)

    def get_content_buffer(self) -> BytesIO:
        """
        Provides a BytesIO object which contains the contents of the file.
        :return: The BytesIO object containing the file contents
        :rtype: BytesIO
        """
        internal_path = join(self.internal_directory, self.filename)
        with self.zip_file.open(internal_path, force_zip64=True) as zip_f:
            buf = BytesIO(zip_f.read())

        return buf

    @staticmethod
    def is_zipped() -> bool:
        return True


class RemoteFileReference(FileReference):
    """
    RemoteFileReference refers to a file held over a network.
    The set_content_buffer methods provides a way for clients of this class to handle the retrieval of file contents from the network.
    """
    def __init__(self, path: str):
        super().__init__(path)
        self.content_buffer: Optional[BytesIO] = None

    def set_content_buffer(self, content_buffer: BytesIO):
        content_buffer.seek(0)
        self.content_buffer = content_buffer

    def get_content_buffer(self) -> BytesIO:
        """
        Provides a BytesIO object which contains the contents of the file.
        :return: The BytesIO object containing the file contents
        :rtype: BytesIO
        """
        if self.content_buffer is None:
            return BytesIO()
        self.content_buffer.seek(0)
        return BytesIO(self.content_buffer.read())


class FileReferenceFactory:
    """
    Implements the Flyweight pattern to mitigate the overhead of re-creating FileReference objects, as the files within
    the file system are expected to change far less frequently than FileReference objects are referred to.
    An add-only cache for FileReference objects is maintained in the form of a dictionary which maps full_path strings
    to the corresponding FileReference object.
    """
    def __init__(self):
        self.file_ref_cache: dict[str, FileReference] = {}

    def clear_cache(self):
        """
        Resets the cache to an empty dictionary
        """
        self.file_ref_cache = {}

    def get_file_refs_from_path(self, path: str, expand_archived: bool) -> list[FileReference]:
        file_refs: list[FileReference]
        curr_file_ref = [self.get_file_ref(path)]
        if path.endswith('.zip'):
            try:
                file_refs = self.get_zip_file_refs(path)
            except BadZipFile:
                return []
            if not expand_archived:
                file_refs = curr_file_ref
        else:
            file_refs = curr_file_ref

        return file_refs

    def get_file_ref(self, path: str) -> FileReference:
        cached_ref: Optional[FileReference] = self.file_ref_cache.get(path)
        if cached_ref is None:
            cached_ref = DiskFileReference(path)
            self.file_ref_cache[path] = cached_ref

        return cached_ref

    def get_zip_file_refs(self, zip_file_path: str) -> list[FileReference]:
        """
        Accepts a zip file and provides a list of FileReference
        objects that correspond to the zipped files within the zip archive.
        :param zip_file_path: the path to the zip archive that holds the files to be listed.
        :return: a list of FileReference objects corresponding to the files within the zip archive
        :rtype: list[FileReference]
        """
        zip_file = ZipFile(zip_file_path)

        file_refs: list[FileReference] = []
        for info in zip_file.infolist():
            if info.is_dir():
                continue
            zip_ref: FileReference = self._get_single_zip_file_ref(zip_file, zip_file_path, info.filename)
            file_refs.append(zip_ref)

        return file_refs

    def _get_single_zip_file_ref(self, zip_file: ZipFile, zip_file_path: str, internal_path: str) -> ZipFileReference:
        full_path: str = join(zip_file_path, internal_path)
        cached_ref: Optional[ZipFileReference] = self.file_ref_cache.get(full_path)
        if cached_ref is None:
            cached_ref = ZipFileReference(zip_file, zip_file_path, internal_path)
            self.file_ref_cache[full_path] = cached_ref

        return cached_ref

    def get_oni_file_ref(self, path: str) -> RemoteFileReference:
        cached_ref: Optional[FileReference] = self.file_ref_cache.get(path)
        if (cached_ref is None) or (type(cached_ref) is not RemoteFileReference):
            cached_ref = RemoteFileReference(path)
            self.file_ref_cache[path] = cached_ref
        cached_ref: RemoteFileReference

        return cached_ref
