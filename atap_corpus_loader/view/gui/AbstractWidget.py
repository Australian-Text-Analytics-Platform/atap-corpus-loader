from abc import ABC, abstractmethod

from panel import Row
from panel.layout import Panel


class AbstractWidget(ABC):
    """
    An abstract class for Panel GUI widgets. Provides methods to set widget visibility and update the display of all
    child widgets.
    """
    def __init__(self):
        self.panel: Panel = Row()
        self.children: list[AbstractWidget] = []

    def __panel__(self) -> Panel:
        return self.panel

    def update_displays(self):
        self.update_display()
        for child in self.children:
            child.update_displays()

    def get_visibility(self) -> bool:
        return self.panel.visible

    def set_visibility(self, is_visible: bool):
        self.panel.visible = is_visible

    def toggle_visibility(self):
        self.panel.visible = not self.panel.visible

    @abstractmethod
    def update_display(self):
        raise NotImplementedError()
