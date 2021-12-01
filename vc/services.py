from typing import Type
from injector import singleton, Binder

from vc import manager, event, event_listener


def bind_singleton(binder: Binder, obj):
    binder.bind(obj, to=obj, scope=singleton)


def managers(binder: Binder):
    # @todo bind_manager with ModelFactory and ModelEventDispatcher
    bind_singleton(binder, manager.GenerationRequestManager)
    bind_singleton(binder, manager.GenerationResultManager)
    bind_singleton(binder, manager.UserManager)


def bind_event_listener(
    binder: Binder,
    vc_event: Type[event.VcEvent],
    vc_event_listener: Type[event_listener.VcEventListener]
):
    bind_singleton(binder, vc_event_listener)
    binder.injector.get(event.VcEventDispatcher).register(
        vc_event.id,
        binder.injector.get(vc_event_listener).on
    )


def events(binder: Binder):
    bind_singleton(binder, event.VcEventDispatcher)
    bind_event_listener(
        binder,
        event.GenerationRequestCreatedEvent,
        event_listener.GenerationRequestCreatedEventListener
    )
    bind_event_listener(
        binder,
        event.GenerationRequestCancelledEvent,
        event_listener.GenerationRequestCancelledEventListener
    )


modules = [
    managers,
    events,
]
