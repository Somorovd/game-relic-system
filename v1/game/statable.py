from .game_manager import Subject


class Statable(Subject):
    def __init__(self):
        super().__init__()
        self.stats = {}

    def has_stat(self, stat_type):
        return stat_type in self.stats

    def get_stat(self, stat_type):
        return self.stats[stat_type].current

    def adjust_stat(self, stat_type, amount):
        self.stats[stat_type].adjust_current(amount)

    def add_stat_source(self, stat_type, source):
        if not stat_type in self.stats:
            self.stats[stat_type] = Stat(stat_type, 0)

        stat = self.stats[stat_type]
        stat.add_source(source)

        def _update_func(event_data):
            if event_data["stat"] != stat_type:
                return

            stat.update_source(source, event_data["amount"])

        source.add_listener("on_stat_update", _update_func)


class Stat(Subject):
    def __init__(self, stat_type, base, current=None):
        super().__init__()
        self.stat_type = stat_type
        self.base = base
        self.current = current or base
        self.mod = 0
        self.sources = {}

    def adjust_current(self, amount):
        self.current += amount
        self._trigger_update()

    def add_source(self, source):
        self.sources[source] = 0

    def update_source(self, source, amount):
        diff = amount - self.sources[source]
        self.mod += diff
        self.current += diff
        self.sources[source] = amount
        self._trigger_update()

    def _trigger_update(self):
        stat_update_event_data = {"stat": self.stat_type, "amount": self.current}
        self.trigger_event("on_stat_update", stat_update_event_data)


class StatModifier(Statable):
    def __init__(self, stat_type, amount):
        super().__init__()
        self.stats[stat_type]
