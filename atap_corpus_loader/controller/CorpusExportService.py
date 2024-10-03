from io import BytesIO, StringIO
from typing import Callable
from zipfile import ZipFile

import numpy as np
from atap_corpus.corpus.corpus import DataFrameCorpus
from pandas import DataFrame, ExcelWriter, Series
from panel.widgets import Tqdm


class CorpusExportService:
    def __init__(self):
        self.export_type_mapping: dict[str, Callable] = {
            'csv': self.export_csv,
            'xlsx': self.export_xlsx,
            'zip': self.export_zip,
            'atap': self.export_serialised_corpus
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
    def _get_normalised_dataframe(corpus: DataFrameCorpus) -> DataFrame:
        return corpus.to_dataframe().astype('string').fillna('')

    @staticmethod
    def export_csv(corpus: DataFrameCorpus, tqdm_obj: Tqdm) -> BytesIO:
        csv_object = BytesIO()
        if len(corpus) == 0:
            return csv_object

        df: DataFrame = CorpusExportService._get_normalised_dataframe(corpus)
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

        df: DataFrame = CorpusExportService._get_normalised_dataframe(corpus)
        chunks = np.array_split(df.index, min(len(df), 1000))
        with tqdm_obj(total=len(df), desc="Exporting to Excel", unit="documents", leave=False) as pbar:
            with ExcelWriter(excel_object, engine="xlsxwriter") as writer:
                df.loc[chunks[0]].to_excel(writer, index=False, header=True)
                pbar.update(len(chunks[0]))
                for chunk, subset in enumerate(chunks[1:]):
                    df.loc[subset].to_excel(writer, startrow=subset[0]+1, index=False, header=False)
                    pbar.update(len(subset))

        return excel_object

    @staticmethod
    def _sanitise_filenames(current_filenames: Series) -> Series:
        remove_chars: list[str] = "\\/:*?\"'<>|".split()
        added_basenames: set[str] = set()
        new_filenames: list[str] = []
        for filename in current_filenames:
            dot_split = filename.split('.')
            if len(dot_split) == 1:
                filename_no_ext = filename
            else:
                filename_no_ext = ''.join(dot_split[:-1])
            sanitised_basename = filename_no_ext
            for char in remove_chars:
                sanitised_basename = sanitised_basename.replace(char, '')
            basename = sanitised_basename
            i = 0
            while basename in added_basenames:
                basename = f"{sanitised_basename}-{i}"
                i += 1
            added_basenames.add(basename)
            filename = f"{basename}.txt"
            new_filenames.append(filename)

        return Series(new_filenames)

    @staticmethod
    def _generate_filenames(root_name: str, num_files: int) -> Series:
        return Series([f"{root_name}-{i}.txt" for i in range(num_files)])

    @staticmethod
    def export_zip(corpus: DataFrameCorpus, tqdm_obj: Tqdm) -> BytesIO:
        zipped_object = BytesIO()
        if len(corpus) == 0:
            return zipped_object

        df: DataFrame = CorpusExportService._get_normalised_dataframe(corpus)
        metas_df: DataFrame = df[corpus.metas]
        filename_col = 'filename'
        if filename_col in metas_df.columns:
            # If the filename metadata exists, preserve it but create a new column with unique filenames
            orig_filename_col = 'original_filename'
            while orig_filename_col in metas_df.columns:
                orig_filename_col += '_'
            orig_filenames = metas_df[filename_col]
            metas_df[filename_col] = CorpusExportService._sanitise_filenames(orig_filenames)
            if not (metas_df[filename_col] == orig_filenames).all():
                # If the old and new filename columns are different, preserve the old column
                metas_df[orig_filename_col] = orig_filenames
        else:
            metas_df[filename_col] = CorpusExportService._generate_filenames(corpus.name, len(corpus))

        zip_file = ZipFile(zipped_object, mode='w')
        for i in tqdm_obj(range(len(corpus)), desc="Exporting to zipped file", unit="documents", leave=False):
            filename = metas_df.loc[i, 'filename']
            document = str(corpus[i])
            zip_file.writestr(filename, document)

        if len(corpus.metas) > 0:
            metadata_buffer = StringIO()
            metas_df.to_csv(metadata_buffer, index=False, mode="w")
            zip_file.writestr('metadata.csv', metadata_buffer.getvalue())
            zip_file.close()

        return zipped_object

    @staticmethod
    def export_serialised_corpus(corpus: DataFrameCorpus, tqdm_obj: Tqdm) -> BytesIO:
        serialised_object = BytesIO()
        for corpus_obj in tqdm_obj([corpus], desc="Exporting to atap file", unit="files", leave=False):
            corpus_obj.serialise(serialised_object)

        return serialised_object
