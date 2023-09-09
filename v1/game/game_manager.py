from collections import defaultdict


class Subject:
    def __init__(self):
        self._listeners = defaultdict(list)
        self._to_remove = defaultdict(list)
        self._is_notifying = False

    def add_listener(self, event_name, listener):
        self._listeners[event_name].append(listener)

    def remove_listener(self, event_name, listener):
        if not self._is_notifying:
            self._listeners[event_name].remove(listener)
        else:
            self._to_remove[event_name].append(listener)

    def trigger_event(self, event_name, event_data):
        data_copy = event_data.copy()  # is this necessarry?
        self._notify(event_name, data_copy)
        return data_copy

    def _notify(self, event_name, event_data):
        self._is_notifying = True
        if not event_name in self._listeners:
            return

        for listener in self._listeners[event_name]:
            listener(event_data)
        self._is_notifying = False
        self._clear_remove_backup()

    def _clear_remove_backup(self):
        for event_name, listeners in self._to_remove.items():
            for listener in listeners:
                self.remove_listener(event_name, listener)
        self._to_remove.clear()


class GameManager(Subject):
    def __init__(self):
        super().__init__()


GAME_MANAGER = GameManager()
