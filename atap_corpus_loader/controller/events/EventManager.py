import logging
import traceback
from typing import Callable, Optional, Union

from atap_corpus_loader.controller.events import EventType


class EventManager:
    """
    An EventManager object maintains a mapping of EventTypes to callable functions.
    When trigger_callbacks is invoked, all registered functions for the provided EventType are called.
    """
    def __init__(self, logger_name: str):
        self.logger_name = logger_name

        self.callback_mapping: dict[EventType, list[Callable]] = {}
        self.reset_callbacks()

    def log(self, msg: str, level: int):
        logger = logging.getLogger(self.logger_name)
        logger.log(level, msg)

    def reset_callbacks(self):
        """
        Removes all callback functions from the event mapping.
        After this method is called, and before further callbacks are registered, the trigger_callbacks will not invoke any callbacks.
        """
        self.callback_mapping = {e: [] for e in EventType}

    def register_event_callback(self, event_type: Union[str, EventType], callback: Callable, first: bool):
        """
        Registers a callback function to execute when the event specified by event_type occurs.
        Multiple callback functions can be registered and will be called in the order added when the event occurs.
        :param event_type: An EventType enum or its corresponding string (case-insensitive) to map the callable to.
        :type event_type: str | EventType
        :param callback: The function that will be invoked when the trigger_callbacks is called with the provided EventType.
        :type callback: Callable
        :param first: If True, the callable will be placed at the start of the queue for the provided EventType. Otherwise, the callable is placed at the end.
        :type first: bool
        """
        if not callable(callback):
            raise TypeError("Provided callback function must be callable")
        if isinstance(event_type, str):
            try:
                event_type = EventType[event_type.upper()]
            except KeyError:
                raise ValueError(f"Provided event_type string does not correspond to an EventType value: {event_type}")
        callback_ls = self.callback_mapping[event_type]
        position = len(callback_ls)
        if first:
            position = 0
        self.callback_mapping[event_type].insert(position, callback)
        self.log(f"New callback registered for event '{event_type.name}'. Callback: {callback}", logging.INFO)

    def trigger_callbacks(self, event_type: Union[str, EventType], *callback_args):
        """
        Triggers all callbacks registered with the given event. Only the specified event will be triggered.
        When a callback raises an exception, the exception will be logged and the subsequent callbacks will be executed.
        :param event_type: an enum with the possible values: LOAD, UNLOAD, BUILD, RENAME, DELETE, UPDATE. String equivalents also accepted
        :type event_type: Union[str, EventType]
        :param callback_args: arguments to pass on to the callbacks being triggered
        :type callback_args: Any
        """
        if isinstance(event_type, str):
            try:
                event_type = EventType[event_type.upper()]
            except KeyError:
                raise ValueError(f"Provided event_type string does not correspond to an EventType value: {event_type}")

        callback_list: Optional[list[Callable]] = self.callback_mapping.get(event_type)
        if callback_list is None:
            raise ValueError(f"No callbacks registered for event type: {event_type.name}")
        for callback in callback_list:
            try:
                callback(*callback_args)
                self.log(f"Callback executed for event '{event_type.name}'. Callback: {callback}", logging.INFO)
            except Exception as e:
                self.log(f"Exception while executing callback for event '{event_type.name}': \n{traceback.format_exc()}", logging.ERROR)
