import time
import random
import hashlib

from typing import Dict
from pydantic import BaseModel, field_validator

from utils.gps import Coordinate, Coordinates


class ConfigTanksDeployment(BaseModel):
    number_of_units: int
    start_latitude: float
    start_longitude: float
    bearing_angle_min: float
    bearing_angle_max: float
    distance_between_units: float
    seconds_between_moves: float
    damage_probability_min: float
    damage_probability_max: float
    damage_impact_min: float
    damage_impact_max: float


class ConfigTanksModelsBase(BaseModel):
    proportion: float
    moving_speed_kph_min: float
    moving_speed_kph_max: float
    ammunition_min: int
    ammunition_max: int
    ammunition_rpm_min: float
    ammunition_rpm_max: float
    damage_can_support_min: float
    damage_can_support_max: float


class ConfigTanksModels(BaseModel):
    data: Dict[str, ConfigTanksModelsBase]


class Tank:
    def __init__(
        self,
        start_point: Coordinate,
        config_deployment: ConfigTanksDeployment,
        config_models: ConfigTanksModels,
    ) -> None:
        self.damage = 0
        self.destroyed = False
        self.current_location = start_point
        self.timestamp = time.time()
        self._coordinates = Coordinates()
        self._config_deployment = config_deployment

        _models = {model: data.proportion for model, data in config_models.data.items()}
        self.model = random.choices(
            list(_models.keys()),
            weights=_models.values(),
            k=1,
        )[0]
        self._model_config = config_models.data[self.model]

        _reference = f"{start_point.lat}_{start_point.lon}_{self.model}"
        self.id = f"tank_{hashlib.sha256(_reference.encode('utf-8')).hexdigest()[:12]}"

        self._supported_damage = (
            random.randint(
                int(self._model_config.damage_can_support_min * 10000),
                int(self._model_config.damage_can_support_max * 10000),
            )
            / 10000
        )

        self.ammo = (
            random.randint(
                int(self._model_config.ammunition_min * 10000),
                int(self._model_config.ammunition_max * 10000),
            )
            / 10000
        )
        self._ammo_shot = 0

        self._bearing_angle = (
            random.randint(
                int(config_deployment.bearing_angle_min * 10000),
                int(config_deployment.bearing_angle_max * 10000),
            )
            / 10000
        )

    def payload_non_transactional(self) -> dict:
        return {
            "id": self.id,
            "model": self.model,
            "timestamp": int(1000 * self.timestamp),
        }

    def payload_transactional(self) -> dict:
        return {
            "id": self.id,
            "lat": self.current_location.lat,
            "lon": self.current_location.lon,
            "timestamp": int(1000 * self.timestamp),
            "ammo": max(int(self.ammo - self._ammo_shot), 0),
            "damage": round(self.damage, 2),
            "current_speed": round(self.speed * 3.6, 2),
            "destroyed": self.destroyed,
        }

    def move(self) -> None:
        timestamp = time.time()

        if self.destroyed:
            self.speed = 0

        else:
            _delta_time = timestamp - self.timestamp

            _rpm = (
                random.randint(
                    int(self._model_config.ammunition_rpm_min * 10000),
                    int(self._model_config.ammunition_rpm_max * 10000),
                )
                / 10000
            )
            if self._ammo_shot < self.ammo:
                self._ammo_shot += _rpm * _delta_time

            self.speed = random.randint(
                int(self._model_config.moving_speed_kph_min * 10000),
                int(self._model_config.moving_speed_kph_max * 10000),
            ) / (3.6 * 10000)
            distance = self.speed * (_delta_time)
            self.current_location = self._coordinates.destination(
                self.current_location,
                self._bearing_angle,
                distance,
            )

            _damage_probability = (
                random.randint(
                    int(self._config_deployment.damage_probability_min * 10000),
                    int(self._config_deployment.damage_probability_max * 10000),
                )
                / 10000
            )

            if _damage_probability > random.random() * 100:
                _damage_impact = (
                    random.randint(
                        int(self._config_deployment.damage_impact_min * 10000),
                        int(self._config_deployment.damage_impact_max * 10000),
                    )
                    / 10000
                )
                self.damage += _damage_impact

                if self.damage > self._supported_damage:
                    self.damage = self._supported_damage
                    self.destroyed = True

        self.timestamp = timestamp
