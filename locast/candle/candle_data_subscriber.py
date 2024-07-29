from abc import ABC
from event_systems.base.event_system import EventSystem
from event_systems.base.event_listener import EventListener
from event_systems.base.handler import Handler

from locast.candle.candle_data_publisher import CandleDataEvent


class CandleDataSubscriber(EventListener, ABC):
    def subscribe_to_candle_cluster_updated(
        self,
        handler: Handler,
        event_system: EventSystem,
    ) -> None:
        event = CandleDataEvent.CANDLE_CLUSTER_UPDATED.value
        subscription = {event: handler}
        self.setup_event_handlers(event_system, subscription)

    def subscribe_to_initial_cluster_update_began(
        self,
        handler: Handler,
        event_system: EventSystem,
    ) -> None:
        event = CandleDataEvent.INITIAL_CLUSTER_UPDATE_BEGAN.value
        subscription = {event: handler}
        self.setup_event_handlers(event_system, subscription)

    def subscribe_to_initial_cluster_update_finished(
        self,
        handler: Handler,
        event_system: EventSystem,
    ) -> None:
        event = CandleDataEvent.INITIAL_CLUSTER_UPDATE_FINISHED.value
        subscription = {event: handler}
        self.setup_event_handlers(event_system, subscription)
