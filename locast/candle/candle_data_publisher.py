from abc import ABC
from enum import Enum
from typing import Any, Dict, List
from event_systems.base.event_system import EventSystem
from locast.candle.candle import Candle


class CandleDataEvent(Enum):
    CANDLE_CLUSTER_UPDATED = "candle_cluster_updated"
    INITIAL_CLUSTER_UPDATE_BEGAN = "cluster_update_began"
    INITIAL_CLUSTER_UPDATE_FINISHED = "cluster_update_finished"


class CandleDataPublisher(ABC):
    def publish_candle_cluster_updated(
        self,
        candle_cluster: List[Candle],
        event_system: EventSystem,
        start_time: float,
    ) -> None:
        event = CandleDataEvent.CANDLE_CLUSTER_UPDATED.value
        event_data: Dict[str, Any] = {
            "candle_cluster": candle_cluster,
            "start_time": start_time,
        }
        event_system.post(event, event_data)

    def publish_initial_cluster_update_began(self, event_system: EventSystem) -> None:
        event = CandleDataEvent.INITIAL_CLUSTER_UPDATE_BEGAN.value
        event_system.post(event, None)

    def publish_initial_cluster_update_finished(
        self,
        event_system: EventSystem,
    ) -> None:
        event = CandleDataEvent.INITIAL_CLUSTER_UPDATE_FINISHED.value
        event_system.post(event, None)
