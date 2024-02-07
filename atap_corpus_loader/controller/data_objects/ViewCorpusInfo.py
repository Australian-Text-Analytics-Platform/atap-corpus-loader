from typing import Optional


class ViewCorpusInfo:
    def __init__(self, corpus_id: str, name: Optional[str], num_rows: int, headers: list[str], dtypes: list[str]):
        self.corpus_id: str = corpus_id
        self.name: Optional[str] = name
        self.num_rows: int = num_rows
        self.headers: list[str] = headers
        self.dtypes: list[str] = dtypes

    def __repr__(self):
        return f"ViewCorpusInfo - id: {self.corpus_id}, name: {self.name}"
