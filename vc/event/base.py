from typing import Callable
from whistle import Event, EventDispatcher


class VcEvent(Event):
    id: str


class VcEventDispatcher:
    dispatcher: EventDispatcher

    def __init__(self):
        self.dispatcher = EventDispatcher()

    def dispatch(self, event: VcEvent):
        self.dispatcher.dispatch(event.id, event)

    def register(self, event_id, fn: Callable):
        self.dispatcher.add_listener(event_id, fn)
