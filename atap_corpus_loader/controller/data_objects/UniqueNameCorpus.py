from datetime import datetime

from atap_corpus.corpus.corpus import DataFrameCorpus
from atap_corpus.registry import _Global_Corpora
from pandas import DataFrame


class UniqueNameCorpus(DataFrameCorpus):
    """
    An internal (package) wrapper class for DataFrameCorpus.
    The only change to DataFrameCorpus is that corpus names must be globally unique.
    The constructor for this class mimics the behaviour of DataFrameCorpus.from_dataframe()
    """
    def __init__(self, df: DataFrame, col_doc: str, name: str):
        if (name == '') or (name is None):
            timestamp = datetime.now()
            self.name = f"Corpus-{timestamp}"
        else:
            self.name = name

        if col_doc not in df.columns:
            raise ValueError(f"Column {col_doc} not found. You must set the col_doc argument.\n"
                             f"Available columns: {df.columns}")
        df = df.copy().reset_index(drop=True)

        super().__init__(df[col_doc], name=self.name)
        col_metas = [c for c in df.columns if c != col_doc]
        for col_meta in col_metas:
            self.add_meta(df.loc[:, col_meta], col_meta)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        if not _Global_Corpora.is_unique_name(name):
            raise ValueError(f"Corpus with name {name} already exists. Select a different name")
        self._name = name
