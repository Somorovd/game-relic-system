from random import random
from enum import Enum

from effect_system.content.event_manager import EventManager


class CardLocation(Enum):
    DECK = 1
    DRAW = 2
    HAND = 3
    DISCARD = 4
    EXHAUST = 5


class CardManager:
    _instance = None

    def __new__(cls):
        if cls._instance:
            return cls._instance
        else:
            cls._instance = super(CardManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self._event_manager = EventManager()
        self.deck = []
        self.draw = []
        self.hand = []
        self.discard = []
        self.exhaust = []

    def reset(self):
        self._initialized = False
        self.__init__()

    def _list_from_location(self, location):
        if location == CardLocation.DECK:
            return self.deck
        elif location == CardLocation.DRAW:
            return self.draw
        elif location == CardLocation.HAND:
            return self.hand
        elif location == CardLocation.DISCARD:
            return self.discard
        elif location == CardLocation.EXHAUST:
            return self.exhaust

    def add_card(self, card, location):
        pre_add_card_event_data = {
            "card": card,
            "type": card.type,
            "cost": card.get_stat("cost"),
            "location": location,
        }
        res = self._event_manager.trigger_event(
            "on_pre_add_card", pre_add_card_event_data
        )

        self._list_from_location(location).append(card)

        post_add_card_event_data = res
        self._event_manager.trigger_event("on_post_add_card", post_add_card_event_data)

    def remove_card(self, card, location):
        pre_remove_card_event_data = {
            "card": card,
            "type": card.type,
            "cost": card.get_stat("cost"),
            "location": location,
        }
        res = self._event_manager.trigger_event(
            "on_pre_remove_card", pre_remove_card_event_data
        )

        self._list_from_location(location).remove(card)

        post_remove_card_event_data = res
        self._event_manager.trigger_event(
            "on_post_remove_card", post_remove_card_event_data
        )

    def shuffle(self):
        self.deck.sort(key=lambda x: random())

    def draw_cards(self, count):
        pre_draw_event_data = {"count": count}
        res = self._event_manager.trigger_event(
            "on_pre_draw_cards", pre_draw_event_data
        )

        cards = self.draw[: res["count"]]
        self.draw = self.draw[res["count"] :]
        self.hand.extend(cards)

        post_draw_event_data = res
        post_draw_event_data.update({"cards": cards})
        res = self._event_manager.trigger_event(
            "on_post_draw_cards", post_draw_event_data
        )
