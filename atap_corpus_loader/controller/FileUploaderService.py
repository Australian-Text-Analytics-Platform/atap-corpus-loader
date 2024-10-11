import os.path


class FileUploadError(Exception):
    pass


class FileUploaderService:
    def __init__(self, root_directory: str):
        self.root_directory: str = root_directory

    def upload_files(self, file_data: dict[str, str | bytes]):
        for filename, file_content in file_data.items():
            filepath: str = os.path.join(self.root_directory, filename)
            if isinstance(file_content, str):
                write_mode = 'w'
            elif isinstance(file_content, bytes):
                write_mode = 'wb'
            else:
                raise FileUploadError(f"Unexpected file contents for file: {filename}")

            try:
                with open(filepath, mode=write_mode) as f:
                    f.write(file_content)
            except OSError as e:
                raise FileUploadError(str(e))
