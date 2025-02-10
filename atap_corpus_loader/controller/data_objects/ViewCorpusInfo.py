from typing import Optional


class ViewCorpusInfo:
    """
    A dataclass that provides a corpus information summary to the view.
    """
    DATA_WIDTH: int = 50

    def __init__(self, name: Optional[str], num_rows: int, parent_name: Optional[str],
                 headers: list[str], dtypes: list[str], first_row_data: list[str]):
        self.name: Optional[str] = name
        self.num_rows: int = num_rows
        self.parent_name: Optional[str] = parent_name
        self.headers: list[str] = headers
        self.dtypes: list[str] = dtypes
        self.first_row_data: list[str] = [x[:ViewCorpusInfo.DATA_WIDTH] for x in first_row_data]

    def __repr__(self):
        return f"ViewCorpusInfo - name: {self.name}"
