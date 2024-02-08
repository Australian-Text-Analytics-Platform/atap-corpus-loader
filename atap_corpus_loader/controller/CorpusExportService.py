from io import BytesIO
from typing import Callable

from pandas import DataFrame


class CorpusExportService:
    def __init__(self):
        self.export_type_mapping: dict[str, Callable] = {
            'csv': self.export_csv,
            'xlsx': self.export_xlsx
        }

    def get_filetypes(self) -> list[str]:
        return list(self.export_type_mapping.keys())

    def export(self, df: DataFrame, filetype: str) -> BytesIO:
        if filetype not in self.export_type_mapping:
            raise ValueError(f"{filetype} is not a valid export format")
        file_object: BytesIO = self.export_type_mapping[filetype](df)
        file_object.seek(0)

        return file_object

    @staticmethod
    def export_csv(df: DataFrame) -> BytesIO:
        csv_object = BytesIO()
        df.to_csv(csv_object, index=False)

        return csv_object

    @staticmethod
    def export_xlsx(df: DataFrame) -> BytesIO:
        excel_object = BytesIO()
        df.to_excel(excel_object, index=False)

        return excel_object
