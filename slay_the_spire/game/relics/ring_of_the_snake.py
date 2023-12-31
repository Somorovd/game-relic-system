from .reqs import Relic
from .reqs import EventDataUpdate, Toggle, EventTrigger, AddOp


class RingOfTheSnake(Relic):
    def __init__(self):
        super().__init__("Ring of the Snake")
        self.add_effect(
            EventDataUpdate("count", AddOp(2)).set_trigger(
                Toggle()
                .set_toggle_on(EventTrigger("on_combat_start"))
                .set_toggle_off(EventTrigger("on_post_draw_cards"))
                .set_trigger(EventTrigger("on_pre_draw_cards"))
            )
        )
