import pathlib
from glob import iglob
from os.path import sep, isdir, basename, join
from typing import Optional

from bokeh.models import Tooltip
from panel.widgets import TooltipIcon



class TooltipManager:
    @staticmethod
    def _resolve_dir(dir_path: str) -> str:
        if type(dir_path) is not str:
            raise TypeError(f"expected string argument, got {type(dir_path)}")
        file_parent = pathlib.Path(__file__).parent.resolve()
        sanitised_directory = join(file_parent, dir_path)
        if not sanitised_directory.endswith(sep):
            sanitised_directory += sep

        return sanitised_directory

    @staticmethod
    def read_markdown_contents() -> dict[str, str]:
        path_pattern: str = f"{TooltipManager.MARKDOWN_DIR}**"
        tooltip_map: dict[str, str] = {}
        for path in iglob(path_pattern, recursive=True):
            if isdir(path):
                continue
            filename_split = basename(path).split('.')
            if len(filename_split) == 1:
                filename = filename_split[0]
            else:
                filename = '.'.join(filename_split[:-1])

            with open(path) as f:
                contents = f.read()
            tooltip_map[filename] = contents

        return tooltip_map

    MARKDOWN_DIR: str = _resolve_dir("./markdown")

    def __init__(self):
        self.tooltip_map: dict[str, str] = self.read_markdown_contents()

    def get_tooltip(self, tooltip_name: str) -> Optional[TooltipIcon]:
        text = self.tooltip_map.get(tooltip_name)
        if text is None:
            return None
        return TooltipIcon(value=text, margin=(0, 0))
