import time

from utils.basemodels import Coordinate, ConfigBasesBase


class Base:
    def __init__(
        self,
        base_id: str,
        config_base: ConfigBasesBase,
    ) -> None:
        self.timestamp = time.time()
        self.id = base_id
        self.name = config_base.name
        self.type = config_base.type
        self.location = Coordinate(
            lat=config_base.latitude,
            lon=config_base.longitude,
        )

    def payload_non_transactional(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "lat": self.location.lat,
            "lon": self.location.lon,
            "timestamp": int(1000 * self.timestamp),
        }
