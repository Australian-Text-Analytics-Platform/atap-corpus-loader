from abc import ABC, abstractmethod
from typing import Callable

from panel import Row, panel, Column
from panel.layout import ListPanel
from panel.widgets import Button


class AbstractWidget(ABC):
    def __init__(self):
        self.component: ListPanel = Row()
        self.children: list[AbstractWidget] = []

    def get_component(self) -> ListPanel:
        return self.component

    def update_displays(self):
        self.update_display()
        for child in self.children:
            child.update_displays()

    def get_visibility(self) -> bool:
        return self.component.visible

    def set_visibility(self, is_visible: bool):
        self.component.visible = is_visible

    def toggle_visibility(self):
        self.component.visible = not self.component.visible

    def create_confirmation_box(self, *args, confirm_callable: Callable):
        def confirm_action(event):
            confirm_callable()
            response.clear()

        def cancel_action(event):
            response.clear()

        confirmation = Button(name='Confirm')
        confirmation.on_click(confirm_action)
        cancel = Button(name='Cancel')
        cancel.on_click(cancel_action)

        response = Column("Are you sure?", Row(confirmation, cancel))
        response.show()

    @abstractmethod
    def update_display(self):
        raise NotImplementedError()
