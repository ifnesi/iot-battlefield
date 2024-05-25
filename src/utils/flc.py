import time
import hashlib

from utils._utils import rand_range_float, random_gauss, format_timestamp
from utils._basemodels import ConfigFLCDeploymentBase


class FLC:
    def __init__(
        self,
        location: str,
        config_flc: ConfigFLCDeploymentBase,
        seconds_between_moves: float,
    ) -> None:
        self.timestamp = time.time()
        self.city = location
        self.id = f"flc_{hashlib.sha256(location.encode('utf-8')).hexdigest()[:12]}"
        self._seconds_between_moves = seconds_between_moves

        self._config_flc = config_flc

        self.ammo = rand_range_float(
            config_flc.ammunition_level_min,
            config_flc.ammunition_level_max,
        )

        self.health = rand_range_float(
            config_flc.health_level_min,
            config_flc.health_level_max,
        )

        self.food = rand_range_float(
            config_flc.food_level_min,
            config_flc.food_level_max,
        )

    def payload_non_transactional(self) -> dict:
        return {
            "id": self.id,
            "city": self.city,
            "lat": self._config_flc.latitude,
            "lon": self._config_flc.longitude,
            "timestamp": format_timestamp(self.timestamp),
        }

    def payload_transactional(self) -> dict:
        return {
            "id": self.id,
            "ammo": int(self.ammo),
            "health": int(self.health),
            "food": int(self.food),
            "timestamp": format_timestamp(self.timestamp),
        }

    def move(self) -> None:
        self.timestamp = time.time()

        self.ammo = random_gauss(
            self.ammo,
            self._config_flc.ammunition_level_var_mean,
            self._config_flc.ammunition_level_var_stdev,
            self._config_flc.ammunition_level_min,
            self._config_flc.ammunition_level_max,
        )

        self.health = random_gauss(
            self.health,
            self._config_flc.health_level_var_mean,
            self._config_flc.health_level_var_stdev,
            self._config_flc.health_level_min,
            self._config_flc.health_level_max,
        )

        self.food = random_gauss(
            self.food,
            self._config_flc.food_level_var_mean,
            self._config_flc.food_level_var_stdev,
            self._config_flc.food_level_min,
            self._config_flc.food_level_max,
        )
