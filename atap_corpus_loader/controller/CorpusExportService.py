from io import BytesIO, StringIO
from typing import Callable
from zipfile import ZipFile

import numpy as np
from atap_corpus.corpus.corpus import DataFrameCorpus
from pandas import DataFrame, ExcelWriter
from panel.widgets import Tqdm


class CorpusExportService:
    def __init__(self):
        self.export_type_mapping: dict[str, Callable] = {
            'csv': self.export_csv,
            'xlsx': self.export_xlsx,
            'zip': self.export_zip
        }

    def get_filetypes(self) -> list[str]:
        return list(self.export_type_mapping.keys())

    def export(self, corpus: DataFrameCorpus, filetype: str, tqdm_obj: Tqdm) -> BytesIO:
        if filetype not in self.export_type_mapping:
            raise ValueError(f"{filetype} is not a valid export format")
        file_object: BytesIO = self.export_type_mapping[filetype](corpus, tqdm_obj)
        file_object.seek(0)

        return file_object

    @staticmethod
    def export_csv(corpus: DataFrameCorpus, tqdm_obj: Tqdm) -> BytesIO:
        csv_object = BytesIO()
        if len(corpus) == 0:
            return csv_object

        df: DataFrame = corpus.to_dataframe()
        chunks = np.array_split(df.index, min(len(df), 1000))
        with tqdm_obj(total=len(df), desc="Exporting to CSV", unit="documents", leave=False) as pbar:
            df.loc[chunks[0]].to_csv(csv_object, mode='w', index=False)
            pbar.update(len(chunks[0]))
            for chunk, subset in enumerate(chunks[1:]):
                df.loc[subset].to_csv(csv_object, header=False, mode='a', index=False)
                pbar.update(len(subset))

        return csv_object

    @staticmethod
    def export_xlsx(corpus: DataFrameCorpus, tqdm_obj: Tqdm) -> BytesIO:
        excel_object = BytesIO()
        if len(corpus) == 0:
            return excel_object

        df: DataFrame = corpus.to_dataframe()
        chunks = np.array_split(df.index, min(len(df), 1000))
        with tqdm_obj(total=len(df), desc="Exporting to Excel", unit="documents", leave=False) as pbar:
            with ExcelWriter(excel_object, engine="xlsxwriter") as writer:
                sheet_name: str = 'Sheet1'
                df.loc[chunks[0]].to_excel(writer, index=False, header=True, sheet_name=sheet_name)

                workbook = writer.book
                worksheet = writer.sheets[sheet_name]

                text_format = workbook.add_format({'num_format': '@'})
                worksheet.set_column(0, len(df.columns) - 1, None, text_format)

                pbar.update(len(chunks[0]))
                for chunk, subset in enumerate(chunks[1:]):
                    df.loc[subset].to_excel(writer, startrow=subset[0]+1, index=False, header=False, sheet_name=sheet_name)
                    pbar.update(len(subset))

        return excel_object

    @staticmethod
    def export_zip(corpus: DataFrameCorpus, tqdm_obj: Tqdm) -> BytesIO:
        zipped_object = BytesIO()
        if len(corpus) == 0:
            return zipped_object

        df: DataFrame = corpus.to_dataframe()
        metas_df: DataFrame = df[corpus.metas]
        filename_col = 'filename'
        while filename_col in metas_df.columns:
            filename_col = filename_col + '_'
        metas_df.rename({'filename': filename_col})
        metas_df['filename'] = ''

        zip_file = ZipFile(zipped_object, mode='w')
        for i in tqdm_obj(range(len(corpus)), desc="Exporting to zipped file", unit="documents", leave=False):
            sanitised_name = "".join(c for c in corpus.name if c.isalpha() or c.isdigit() or c == ' ').rstrip()
            filename = f"{sanitised_name}-{i + 1}.txt"
            document = str(corpus[i])
            zip_file.writestr(filename, document)
            metas_df.loc[i, 'filename'] = filename

        if len(corpus.metas) > 0:
            metadata_buffer = StringIO()
            metas_df.to_csv(metadata_buffer, index=False, mode="w")
            zip_file.writestr('metadata.csv', metadata_buffer.getvalue())
            zip_file.close()

        return zipped_object
