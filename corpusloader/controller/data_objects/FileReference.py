from os.path import join, relpath, dirname, basename
from zipfile import ZipFile


class FileReference:
    def __init__(self, root_directory: str, directory_path: str, filename: str):
        self.root_directory: str = root_directory
        self.directory_path: str = directory_path
        self.filename: str = filename

        self.file = None

    def __eq__(self, other):
        if not isinstance(other, FileReference):
            return False
        return self.get_full_path() == other.get_full_path()

    def __hash__(self):
        return hash(self.get_full_path())

    def __str__(self):
        return self.get_full_path()

    def __repr__(self):
        return self.get_full_path()

    def __enter__(self):
        self.file = open(self.get_full_path())
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()

    def get_full_path(self) -> str:
        return join(self.directory_path, self.filename)

    def get_directory_path(self):
        return self.directory_path

    def get_filename(self) -> str:
        return self.filename

    def get_relative_path(self):
        return relpath(self.get_full_path(), self.root_directory)

    def is_zipped(self) -> bool:
        return False


class ZipFileReference(FileReference):
    @staticmethod
    def get_zip_internal_file_refs(root_directory: str, zip_file_path: str) -> list[FileReference]:
        with ZipFile(zip_file_path) as zip_f:
            info_list = zip_f.infolist()

        file_refs: list[FileReference] = []
        for info in info_list:
            if info.is_dir():
                continue
            internal_directory: str = dirname(info.filename)
            filename: str = basename(info.filename)
            zip_ref: FileReference = ZipFileReference(root_directory, zip_file_path, internal_directory, filename)
            file_refs.append(zip_ref)

        return file_refs

    def __init__(self, root_directory: str, zip_file_path: str, internal_directory: str, filename: str):
        super().__init__(root_directory, zip_file_path, filename)
        self.internal_directory: str = internal_directory

        self.zip_file = None

    def __enter__(self):
        internal_path = join(self.internal_directory, self.filename)
        self.zip_file = ZipFile(self.directory_path)
        self.file = self.zip_file.open(internal_path, force_zip64=True)
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        self.zip_file.close()
        self.file.close()

    def get_zip_file_path(self) -> str:
        return self.directory_path

    def get_full_path(self) -> str:
        return join(self.directory_path, self.internal_directory, self.filename)

    def is_zipped(self) -> bool:
        return True
