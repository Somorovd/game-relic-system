from abc import ABC, abstractmethod
from collections import defaultdict


class EventManager:
    def __init__(self):
        self._listeners = defaultdict(list)

    def add_listener(self, event_name, listener):
        self._listeners[event_name].append(listener)

    def remove_listener(self, event_name, listener):
        self._listeners[event_name].remove(listener)

    def notify(self, event_name, event_data):
        if not event_name in self._listeners:
            return

        for listener in self._listeners[event_name]:
            if listener.validate(event_data):
                listener.activate(event_data)


class Listener(ABC):
    @abstractmethod
    def activate(self, event_data):
        pass

    @abstractmethod
    def validate(self, event_data):
        pass
