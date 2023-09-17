from .game_manager import GAME_MANAGER, Subject
from .targeters import *


class Effect:
    def __init__(self):
        self.relic = None
        self.validators = []
        self.targeters = []

    def add_event_validator(self, validator):
        self.validators.append(validator)
        return self

    def validate(self, event_data):
        return all([v.validate(self, event_data) for v in self.validators])

    def add_targeters(self, targeters):
        if isinstance(targeters, list):
            self.targeters.extend(targeters)
        else:
            self.targeters.append(targeters)
        return self

    def on_add_to_relic(self, relic, event_name):
        self.relic = relic
        self.event_name = event_name

    def on_equip(self, player):
        pass

    def on_unequip(self, player):
        pass

    def update(self, event_data):
        if self.validate(event_data):
            self.activate(event_data)

    def activate(self, event_data):
        for targerter in self.targeters:
            for target in targerter.get_targets(self, event_data):
                self._apply(event_data, target)

    def _apply(self, event_data, target):
        pass


class EventDataUpdate(Effect):
    def __init__(self, data_type, amount):
        super().__init__()
        self.data_type = data_type
        self.amount = amount
        self.add_targeters(event_data_targeter)

    def _apply(self, event_data, target):
        print(
            f"{self.relic.name} increasing {self.data_type} from {target[self.data_type]} to {target[self.data_type] + self.amount}"
        )
        target[self.data_type] += self.amount


# class StatUpdate(Effect):
#     def __init__(self, stat_type, amount):
#         super().__init__()
#         self.stat_type = stat_type
#         self.amount = amount

#     def activate(self, event_data):
#         print(
#             f"{self.relic.name} is updating {self.stat_type} on {self.relic.player.name} from {self.amount} to {self.relic.player.stats[self.stat_type] + self.amount}"
#         )
#         self.relic.player.updateStat(self.stat_type, self.amount)


class Heal(Effect):
    def __init__(self, amount):
        super().__init__()
        self.amount = amount

    def _apply(self, event_data, target):
        print(f"{self.relic.name} is healing {target.name} for {self.amount}")
        target.apply_healing(self.amount)


class Counter(Effect):
    def __init__(self, max_count, effect):
        super().__init__()
        self.effect = effect
        self.max_count = max_count
        self.curr_count = 0

    def on_add_to_relic(self, relic, event_name):
        super().on_add_to_relic(relic, event_name)
        self.effect.on_add_to_relic(relic, event_name)

    def on_equip(self, player):
        super().on_equip(player)
        self.effect.on_equip(player)

    def activate(self, event_data):
        self.curr_count += 1
        print(
            f"{self.relic.name} increases count by 1. Now at {self.curr_count}/{self.max_count}"
        )

        if self.curr_count >= self.max_count:
            print(f"{self.relic.name} cowntdown complete. Activating...")
            self.effect.activate(event_data)
            self.curr_count = 0


class NTimes(Effect):
    def __init__(self, max_count, effect):
        super().__init__()
        self.effect = effect
        self.max_count = max_count
        self.curr_count = 0

    def on_add_to_relic(self, relic, event_name):
        super().on_add_to_relic(relic, event_name)
        self.effect.on_add_to_relic(relic, event_name)

    def on_equip(self, player):
        super().on_equip(player)
        self.effect.on_equip(player)

    def activate(self, event_data):
        self.curr_count += 1
        self.effect.activate(event_data)
        if self.curr_count >= self.max_count:
            GAME_MANAGER.remove_listener(self.event_name, self.update)


class StatModifier(Subject, Effect):
    def __init__(self, stat_type, amount):
        super().__init__()
        self.stat_type = stat_type
        self.amount = amount

    def on_add_to_relic(self, relic, event_name):
        super().on_add_to_relic(relic, event_name)
        self.relic.add_stat_source(self.stat_type, self)

    def on_equip(self, player):
        for targerter in self.targeters:
            for target in targerter.get_targets(self, None):
                target.add_stat_source(self.stat_type, self.relic)

    def activate(self, event_data):
        print(
            f"{self.relic.name} is modifying {self.stat_type} by {self.amount} on {self.relic.player.name}"
        )
        stat_update_event_data = {"stat": self.stat_type, "amount": self.amount}
        self.trigger_event("on_stat_update", stat_update_event_data)


"""
Relic("Hawk Eye")
  .add_effect(
    "on_player_add_relic",
    NTimes(1,
      StatModifier("max_count", -1)
        .add_targeter(attached_player_relics_targeter)
    )
      .add_validator(AttachedPlayerValidator())
  )
  .add_effect(
    "on_player_add_relic",
    StatModifier("max-count", -1)
      .add_targeter(EventDataPropertyTargeter("relic"))
      .add_validator(
        PropertyEquals("relic", attached_relic_targeter).invert()
      )
  )
"""


class ChangeRelicTiming(Effect):
    # could have a different one to set to a specific value
    # may need to specify type of counter / counting property
    def __init__(self, amount):
        super().__init__()
        self.amount = amount
        self.affected_effects = []

    def modify_relic_effect(self, relic, effect):
        if not type(effect) == Counter:
            return

        prev = effect.max_count
        effect.max_count = max(0, effect.max_count + self.amount)
        curr = effect.max_count
        print(
            f"Updating {effect.property} counter on {relic.name} from {prev} to {curr}"
        )
        self.affected_effects.append(effect)

    def on_equip(self, player):
        for relic in player.relics:
            for effect in relic.effects:
                self.modify_relic_effect(relic, effect)

    def on_unequip(self, player):
        for effect in self.affected_effects:
            effect.count = max(0, effect.max_count - self.amount)
        self.affected_effects = []

    def activate(self, event_data):
        # event is an on_player_add_relic
        relic = event_data.get("relic")
        if not relic:
            return

        for effect in relic.effects:
            self.modify_relic_effect(relic, effect)
