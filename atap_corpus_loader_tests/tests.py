import sys
import unittest
import os
from typing import Optional

from atap_corpus.corpus.corpus import DataFrameCorpus
from pandas import DataFrame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from atap_corpus_loader import CorpusLoader
from atap_corpus_loader.view.gui import FileLoaderWidget, FileSelectorWidget, MetaEditorWidget


class TestFileTypes(unittest.TestCase):
    TEST_DIR: str = str(os.path.join(os.path.dirname(__file__), 'test_data'))
    META_LINKING_HEADER: str = "filename"
    EXPECTED_DATA: dict = {
        "document_": [
            "Plato, a student of Socrates, founded the Academy in Athens and is renowned for his contributions to metaphysics, epistemology, and political philosophy. Born around 428 BCE and living until approximately 348 BCE, Plato\'s dialogues, including \"The Republic,\" explored the nature of reality, the theory of forms, and the ideal state. Socrates was his most influential teacher.",
            "Socrates, often considered the father of Western philosophy, was an ancient Greek philosopher who focused on ethics and the pursuit of knowledge through dialogue. He believed in the importance of questioning and self-examination, famously saying, \"The unexamined life is not worth living.\" Born around 470 BCE in Athens, Socrates did not leave behind any written records of his teachings. His most influential teacher was thought to be Archelaus.",
            "A pupil of Plato, Aristotle became one of history\'s most significant thinkers. Born in 384 BCE in Stagira, he contributed extensively to philosophy, science, and ethics. His works encompass a wide range of topics, from metaphysics and ethics to politics and biology. Aristotle\'s emphasis on observation and empirical reasoning laid the groundwork for scientific inquiry. Plato was his most influential teacher.",
            "Pythagoras, born around 570 BCE, was a mathematician and philosopher best known for the Pythagorean theorem in geometry. His teachings extended to metaphysics, cosmology, and the idea of mathematical relationships governing the universe. Pythagoras founded a religious movement that influenced later philosophical and mathematical thought. His most influential teacher is believed to be Anaximander.",
            "Heraclitus, born around 535 BCE in Ephesus, focused on metaphysics and the nature of change. He is famous for the concept that \"you cannot step into the same river twice,\" emphasizing the constant flux of the universe. Heraclitus believed in the unity of opposites and the transformative nature of fire. While his work is fragmentary, it has influenced later philosophers. His most influential teacher is not definitively known."
        ],
        "philosopher_name": ["Plato", "Socrates", "Aristotle", "Pythagoras", "Heraclitus"],
        "birth_year": [-428, -470, -384, -570, -535],
        "teacher": ["Socrates", "Archelaus", "Plato", "Anaximander", "unknown"]
    }
    EXPECTED_DATA_TYPES: dict = {
        "document_": "string",
        "philosopher_name": "string",
        "birth_year": "int64",
        "teacher": "string"
    }

    def _sort_df(self, df: DataFrame) -> DataFrame:
        df = df.sort_values(by='philosopher_name', ignore_index=True)
        df = df.astype(dtype=TestFileTypes.EXPECTED_DATA_TYPES)

        return df

    def setUp(self):
        self.corpus_loader: CorpusLoader = CorpusLoader(TestFileTypes.TEST_DIR)
        self.expected_df: DataFrame = DataFrame(TestFileTypes.EXPECTED_DATA)
        for col_name, dtype in TestFileTypes.EXPECTED_DATA_TYPES.items():
            self.expected_df[col_name] = self.expected_df[col_name].astype(dtype)
        # Rows can be in any order
        self.expected_df = self._sort_df(self.expected_df)

    def _test_file_filter(self, corpus_filter: str, meta_filter: Optional[str]):
        file_loader_widget: FileLoaderWidget = self.corpus_loader.view.file_loader
        file_selector_widget: FileSelectorWidget = file_loader_widget.file_selector
        meta_editor_widget: MetaEditorWidget = file_loader_widget.meta_editor

        # Load corpus files
        file_selector_widget.filter_input.value = corpus_filter
        file_selector_widget.update_display()
        file_selector_widget.select_all()
        file_loader_widget.load_as_corpus()
        file_loader_widget.update_displays()

        self.assertTrue(len(self.corpus_loader.controller.get_corpus_headers()) > 0,
                        "Expected more than 0 headers, got 0")

        text_header = self.corpus_loader.controller.get_corpus_headers()[0].name
        meta_editor_widget._set_text_header(text_header)

        if meta_filter is not None:
            # Load meta files if filter provided
            file_selector_widget.filter_input.value = meta_filter
            file_selector_widget.update_displays()
            file_selector_widget.select_all()
            file_loader_widget.load_as_meta()
            meta_editor_widget.corpus_link_dropdown.value = TestFileTypes.META_LINKING_HEADER
            meta_editor_widget.meta_link_dropdown.value = TestFileTypes.META_LINKING_HEADER

        # Build the corpus
        file_loader_widget.build_corpus()

        # Compare the resulting DataFrame to the expected DataFrame
        corpus: DataFrameCorpus = self.corpus_loader.get_corpus()
        self.assertIsNotNone(corpus)
        corpus_df: DataFrame = corpus.to_dataframe()
        # Drop filename and filepath columns as these are too changeable to test easily
        corpus_df = corpus_df.drop(labels=['filename', 'filepath'],
                                   axis='columns', errors='ignore')
        # Rows can be in any order
        corpus_df = self._sort_df(corpus_df)

        if not self.expected_df.equals(corpus_df):
            assert False, "Expected corpus differs from built corpus"

    def test_csv_corpus(self):
        corpus_filter: str = "test_data/csv_corpus/philosophers.csv"
        self._test_file_filter(corpus_filter, None)

    def test_csv_meta_txt_corpus(self):
        corpus_filter: str = "test_data/txt_corpus/*"
        meta_filter: str = "test_data/csv_split_meta/*"
        self._test_file_filter(corpus_filter, meta_filter)

    def test_xlsx_meta_docx_corpus(self):
        corpus_filter: str = "test_data/docx_corpus/*"
        meta_filter: str = "test_data/xlsx_meta/*"
        self._test_file_filter(corpus_filter, meta_filter)

    def test_ods_corpus(self):
        corpus_filter: str = "test_data/ods_corpus/*"
        self._test_file_filter(corpus_filter, None)

    def test_ods_meta_odt_corpus(self):
        corpus_filter: str = "test_data/odt_corpus/*"
        meta_filter: str = "test_data/ods_meta/*"
        self._test_file_filter(corpus_filter, meta_filter)

    def test_tsv_meta_txt_corpus(self):
        corpus_filter: str = "test_data/txt_corpus/*"
        meta_filter: str = "test_data/tsv_meta/*"
        self._test_file_filter(corpus_filter, meta_filter)

    def test_xlsx_corpus(self):
        corpus_filter: str = "test_data/xlsx_corpus/*"
        self._test_file_filter(corpus_filter, None)

    def test_rda_corpus(self):
        corpus_filter: str = "test_data/rda_corpus/*"
        self._test_file_filter(corpus_filter, None)

    def test_rdata_corpus(self):
        corpus_filter: str = "test_data/rdata_corpus/*"
        self._test_file_filter(corpus_filter, None)

    def test_rds_corpus(self):
        corpus_filter: str = "test_data/rds_corpus/*"
        self._test_file_filter(corpus_filter, None)

    def test_csv_corpus_zip(self):
        corpus_filter: str = "test_data/csv_corpus.zip"
        self._test_file_filter(corpus_filter, None)

    def test_csv_meta_txt_corpus_zip(self):
        corpus_filter: str = "test_data/txt_corpus.zip"
        meta_filter: str = "test_data/csv_split_meta.zip"
        self._test_file_filter(corpus_filter, meta_filter)

    def test_xlsx_meta_docx_corpus_zip(self):
        corpus_filter: str = "test_data/docx_corpus.zip"
        meta_filter: str = "test_data/xlsx_meta.zip"
        self._test_file_filter(corpus_filter, meta_filter)

    def test_ods_corpus_zip(self):
        corpus_filter: str = "test_data/ods_corpus.zip"
        self._test_file_filter(corpus_filter, None)

    def test_ods_meta_odt_corpus_zip(self):
        corpus_filter: str = "test_data/odt_corpus.zip"
        meta_filter: str = "test_data/ods_meta.zip"
        self._test_file_filter(corpus_filter, meta_filter)

    def test_tsv_meta_txt_corpus_zip(self):
        corpus_filter: str = "test_data/txt_corpus.zip"
        meta_filter: str = "test_data/tsv_meta.zip"
        self._test_file_filter(corpus_filter, meta_filter)

    def test_xlsx_corpus_zip(self):
        corpus_filter: str = "test_data/*xlsx_corpus.zip"
        self._test_file_filter(corpus_filter, None)

    def test_rda_corpus_zip(self):
        corpus_filter: str = "test_data/*rda_corpus.zip"
        self._test_file_filter(corpus_filter, None)

    def test_rdata_corpus_zip(self):
        corpus_filter: str = "test_data/*rdata_corpus.zip"
        self._test_file_filter(corpus_filter, None)

    def test_rds_corpus_zip(self):
        corpus_filter: str = "rds_corpus.zip"
        self._test_file_filter(corpus_filter, None)


if __name__ == '__main__':
    unittest.main()
