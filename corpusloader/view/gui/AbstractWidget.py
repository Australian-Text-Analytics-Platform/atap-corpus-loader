from abc import ABC, abstractmethod


class AbstractWidget(ABC):
    @abstractmethod
    def get_component(self):
        raise NotImplementedError()

    @abstractmethod
    def update_displays(self):
        raise NotImplementedError()

    @abstractmethod
    def set_visibility(self, is_visible: bool):
        raise NotImplementedError()

    @abstractmethod
    def toggle_visibility(self):
        raise NotImplementedError()
