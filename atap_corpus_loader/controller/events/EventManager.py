import traceback
from typing import Callable, Optional

from atap_corpus_loader.controller.events import EventType


class EventManager:
    def __init__(self, logger):
        self.logger = logger

        self.callback_mapping: dict[EventType, list[Callable]] = {}
        self.reset_callbacks()

    def reset_callbacks(self):
        self.callback_mapping = {e: [] for e in EventType}

    def register_event_callback(self, event_type: EventType, callback: Callable):
        if not callable(callback):
            raise TypeError("Provided callback function must be callable")
        self.callback_mapping[event_type].append(callback)
        self.logger.info(f"New callback registered for event '{event_type.name}'. Callback: {callback}")

    def trigger_callbacks(self, event_type: EventType, *callback_args):
        callback_list: Optional[list[Callable]] = self.callback_mapping.get(event_type)
        if callback_list is None:
            raise ValueError(f"No callbacks registered for event type: {event_type.name}")
        for callback in callback_list:
            try:
                callback(*callback_args)
                self.logger.info(f"Callback executed for event '{event_type.name}'. Callback: {callback}")
            except Exception as e:
                self.logger.exception(f"Exception while executing callback for event '{event_type.name}': {type(e)}\n{traceback.format_exc()}")
