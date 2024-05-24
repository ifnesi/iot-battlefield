import time
import random
import hashlib

from utils.basemodels import ConfigFLCDeploymentBase


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

        self.ammo = (
            random.randint(
                int(config_flc.ammunition_level_min * 10000),
                int(config_flc.ammunition_level_max * 10000),
            )
            / 10000
        )

        self.health = (
            random.randint(
                int(config_flc.health_level_min * 10000),
                int(config_flc.health_level_max * 10000),
            )
            / 10000
        )

        self.food = (
            random.randint(
                int(config_flc.food_level_min * 10000),
                int(config_flc.food_level_max * 10000),
            )
            / 10000
        )

    def payload_non_transactional(self) -> dict:
        return {
            "id": self.id,
            "city": self.city,
            "lat": self._config_flc.latitude,
            "lon": self._config_flc.longitude,
            "timestamp": int(1000 * self.timestamp),
        }

    def payload_transactional(self) -> dict:
        return {
            "id": self.id,
            "ammo": int(self.ammo),
            "health": int(self.health),
            "food": int(self.food),
            "timestamp": int(1000 * self.timestamp),
        }

    def move(self) -> None:
        self.timestamp = time.time()

        self.ammo += (
            random.randint(
                int(self._config_flc.ammunition_level_var_min * 10000),
                int(self._config_flc.ammunition_level_var_max * 10000),
            )
            / 10000
        )
        self.ammo = min(
            max(
                self.ammo,
                self._config_flc.ammunition_level_min,
            ),
            self._config_flc.ammunition_level_max,
        )

        self.health += (
            random.randint(
                int(self._config_flc.health_level_var_min * 10000),
                int(self._config_flc.health_level_var_max * 10000),
            )
            / 10000
        )
        self.health = min(
            max(
                self.health,
                self._config_flc.health_level_min,
            ),
            self._config_flc.health_level_max,
        )

        self.food += (
            random.randint(
                int(self._config_flc.food_level_var_min * 10000),
                int(self._config_flc.food_level_var_max * 10000),
            )
            / 10000
        )
        self.food = min(
            max(
                self.food,
                self._config_flc.food_level_min,
            ),
            self._config_flc.food_level_max,
        )
