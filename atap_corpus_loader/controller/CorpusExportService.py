from io import BytesIO
from typing import Callable

import numpy as np
from pandas import DataFrame, ExcelWriter
from panel.widgets import Tqdm


class CorpusExportService:
    def __init__(self):
        self.export_type_mapping: dict[str, Callable] = {
            'csv': self.export_csv,
            'xlsx': self.export_xlsx
        }

    def get_filetypes(self) -> list[str]:
        return list(self.export_type_mapping.keys())

    def export(self, df: DataFrame, filetype: str, tqdm_obj: Tqdm) -> BytesIO:
        if filetype not in self.export_type_mapping:
            raise ValueError(f"{filetype} is not a valid export format")
        file_object: BytesIO = self.export_type_mapping[filetype](df, tqdm_obj)
        file_object.seek(0)

        return file_object

    @staticmethod
    def export_csv(df: DataFrame, tqdm_obj: Tqdm) -> BytesIO:
        csv_object = BytesIO()
        chunks = np.array_split(df.index, min(len(df), 1000))
        with tqdm_obj(total=len(df), desc="Exporting to CSV", unit="documents", leave=False) as pbar:
            df.loc[chunks[0]].to_csv(csv_object, mode='w', index=False)
            pbar.update(len(chunks[0]))
            for chunk, subset in enumerate(chunks[1:]):
                df.loc[subset].to_csv(csv_object, header=None, mode='a', index=False)
                pbar.update(len(subset))

        return csv_object

    @staticmethod
    def export_xlsx(df: DataFrame, tqdm_obj: Tqdm) -> BytesIO:
        excel_object = BytesIO()
        if len(df) == 0:
            return excel_object

        chunks = np.array_split(df.index, min(len(df), 1000))
        with tqdm_obj(total=len(df), desc="Exporting to Excel", unit="documents", leave=False) as pbar:
            with ExcelWriter(excel_object) as writer:
                df.loc[chunks[0]].to_excel(writer, index=False, header=True, sheet_name='Sheet1')
                pbar.update(len(chunks[0]))
                for chunk, subset in enumerate(chunks[1:]):
                    df.loc[subset].to_excel(writer, startrow=subset[0]+1, index=False, header=False, sheet_name='Sheet1')
                    pbar.update(len(subset))

        return excel_object
