import time
import random
import hashlib

from utils._utils import rand_range_float, format_timestamp, Coordinates
from utils._basemodels import Coordinate, ConfigTanksDeployment, ConfigTanksModels


class Tank:
    def __init__(
        self,
        start_point: Coordinate,
        config_deployment: ConfigTanksDeployment,
        config_models: ConfigTanksModels,
    ) -> None:
        self.timestamp = time.time()
        self.damage = 0
        self._ammo_shot = 0
        self.destroyed = False
        self.current_location = start_point
        self._coordinates = Coordinates()
        self._config_deployment = config_deployment

        _models = {model: data.proportion for model, data in config_models.data.items()}
        self.model = random.choices(
            list(_models.keys()),
            weights=_models.values(),
            k=1,
        )[0]
        self._model_config = config_models.data[self.model]

        _reference = (
            f"{start_point.lat}_{start_point.lon}_{self.model}_{random.random()}"
        )
        self.id = f"tank_{hashlib.sha256(_reference.encode('utf-8')).hexdigest()[:12]}"

        self._supported_damage = rand_range_float(
            self._model_config.damage_can_support_min,
            self._model_config.damage_can_support_max,
        )

        self.ammo = rand_range_float(
            self._model_config.ammunition_min,
            self._model_config.ammunition_max,
        )

        self._bearing_angle = rand_range_float(
            config_deployment.bearing_angle_min,
            config_deployment.bearing_angle_max,
        )

    def payload_non_transactional(self) -> dict:
        return {
            "id": self.id,
            "model": self.model,
            "timestamp": format_timestamp(self.timestamp),
        }

    def payload_transactional(self) -> dict:
        return {
            "id": self.id,
            "lat": self.current_location.lat,
            "lon": self.current_location.lon,
            "ammo": int(max(self.ammo - self._ammo_shot, 0)),
            "damage": round(self.damage, 2),
            "current_speed": round(self.speed * 3.6, 2),
            "destroyed": self.destroyed,
            "timestamp": format_timestamp(self.timestamp),
        }

    def move(self) -> None:
        timestamp = time.time()

        if self.destroyed:
            self.speed = 0

        else:
            _delta_time = timestamp - self.timestamp

            _rpm = rand_range_float(
                self._model_config.ammunition_rpm_min,
                self._model_config.ammunition_rpm_max,
            )
            if self._ammo_shot < self.ammo:
                self._ammo_shot += _rpm * _delta_time

            self.speed = (
                rand_range_float(
                    self._model_config.moving_speed_kph_min,
                    self._model_config.moving_speed_kph_max,
                )
                / 3.6
            )
            distance = self.speed * _delta_time
            self.current_location = self._coordinates.destination(
                self.current_location,
                self._bearing_angle,
                distance,
            )

            _damage_probability = rand_range_float(
                self._config_deployment.damage_probability_min,
                self._config_deployment.damage_probability_max,
            )

            if _damage_probability > random.random() * 100:
                _damage_impact = rand_range_float(
                    self._config_deployment.damage_impact_min,
                    self._config_deployment.damage_impact_max,
                )
                self.damage += _damage_impact

                if self.damage > self._supported_damage:
                    self.damage = self._supported_damage
                    self.destroyed = True
                    self.speed = 0

        self.timestamp = timestamp
