from typing import Optional


class ViewCorpusInfo:
    def __init__(self, name: Optional[str], num_rows: int, headers: list[str], dtypes: list[str]):
        self.name: Optional[str] = name
        self.num_rows: int = num_rows
        self.headers: list[str] = headers
        self.dtypes: list[str] = dtypes

    def __repr__(self):
        return f"ViewCorpusInfo - name: {self.name}"
