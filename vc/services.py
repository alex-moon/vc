from typing import Type
from injector import singleton, Binder

from vc import manager, service, event, event_listener


def bind_singleton(binder: Binder, obj):
    binder.bind(obj, to=obj, scope=singleton)


def managers(binder: Binder):
    # @todo bind_manager with ModelFactory and ModelEventDispatcher
    bind_singleton(binder, manager.GenerationRequestManager)


def services(binder: Binder):
    # @todo none of this is necessary apparently...?
    bind_singleton(binder, service.ApiProvider)
    bind_singleton(binder, service.QueueService)
    bind_singleton(binder, service.JobService)
    bind_singleton(binder, service.JobSerializer)
    bind_singleton(binder, service.FileService)


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


modules = [
    managers,
    services,
    events,
]
