from typing import Optional


class ViewCorpusInfo:
    DATA_WIDTH: int = 50
    def __init__(self, name: Optional[str], num_rows: int,
                 headers: list[str], dtypes: list[str], first_row_data: list[str]):
        self.name: Optional[str] = name
        self.num_rows: int = num_rows
        self.headers: list[str] = headers
        self.dtypes: list[str] = dtypes
        self.first_row_data: list[str] = [x[:ViewCorpusInfo.DATA_WIDTH] for x in first_row_data]

    def __repr__(self):
        return f"ViewCorpusInfo - name: {self.name}"
