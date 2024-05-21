import time
import random

from faker import Faker
from typing import Dict
from pydantic import BaseModel, field_validator

from utils.gps import Coordinate, Coordinates


class ConfigTroopsGeneral(BaseModel):
    normal_pulse_rate_min: int
    normal_pulse_rate_max: int
    normal_body_temperature_min: float
    normal_body_temperature_max: float
    bmi_min: float
    bmi_max: float
    height_min: int
    height_max: int
    deceased_if_pulse_rate_under: float
    deceased_if_body_temperature_under: float


class ConfigTroopsDeployment(BaseModel):
    number_of_troops: int
    start_latitude: float
    start_longitude: float
    bearing_angle_min: int
    bearing_angle_max: int
    moving_speed_kph_min: float
    moving_speed_kph_max: float
    troops_distance_between: float
    seconds_between_moves: float


class ConfigTroopsBloodTypes(BaseModel):
    data: Dict[str, float]


class ConfigTroopsRanks(BaseModel):
    data: Dict[str, float]


class ConfigTroopsInjuryBase(BaseModel):
    probability: float
    death_minutes: float
    pulse_rate_surge: float
    body_temperature_drop: float
    moving_speed_kph: float


class ConfigTroopsInjury(BaseModel):
    data: Dict[str, ConfigTroopsInjuryBase]
    @field_validator("data")
    def add_no_injury(cls, data):
        sum_prob = sum(value.probability for value in data.values())
        data[None] = ConfigTroopsInjuryBase(
            probability=100-sum_prob,
            death_minutes=0,
            pulse_rate_surge=0,
            body_temperature_drop=0,
            moving_speed_kph=0,
        )
        return data

class Troop:
    def __init__(
        self,
        start_point: Coordinate,
        config_general: ConfigTroopsGeneral,
        config_deployment: ConfigTroopsDeployment,
        config_blood_types: ConfigTroopsBloodTypes,
        config_ranks: ConfigTroopsRanks,
        config_injury: ConfigTroopsInjury,
    ) -> None:
        self.deceased = False
        self.injury = None
        self.injury_time = None
        self.current_location = start_point
        self.timestamp = time.time()
        self._coordinates = Coordinates()
        self._config_general = config_general
        self._config_deployment = config_deployment
        self._config_injury = config_injury
        self._injuries = {
            injury: data.probability for injury, data in config_injury.data.items()
        }

        f = Faker()
        self.id = f"troop_{random.randint(1000000, 9999999)}"
        self.name = f.name()

        bmi = (
            random.randint(
                int(config_general.bmi_min * 100),
                int(config_general.bmi_max * 100),
            )
            / 100
        )
        self.height = (
            random.randint(
                int(config_general.height_min * 100),
                int(config_general.height_max * 100),
            )
            / 100
        )
        self.weight = round(bmi * (self.height/100)**2, 2)

        self.rank = random.choices(
            list(config_ranks.data.keys()),
            weights=config_ranks.data.values(),
            k=1,
        )[0]

        self.blood_type = random.choices(
            list(config_blood_types.data.keys()),
            weights=config_blood_types.data.values(),
            k=1,
        )[0]

        self.body_temperature = (
            random.randint(
                int(config_general.normal_body_temperature_min * 100),
                int(config_general.normal_body_temperature_max * 100),
            )
            / 100
        )
        self.pulse_rate = (
            random.randint(
                int(config_general.normal_pulse_rate_min * 100),
                int(config_general.normal_pulse_rate_max * 100),
            )
            / 100
        )
        self._bearing_angle = (
            random.randint(
                int(config_deployment.bearing_angle_min * 100),
                int(config_deployment.bearing_angle_max * 100),
            )
            / 100
        )

    def payload_non_transactional(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "weight": self.weight,
            "blood_type": self.blood_type,
            "rank": self.rank,
        }

    def payload_transactional(self) -> dict:
        return {
            "id": self.id,
            "lat": self.current_location.lat,
            "lon": self.current_location.lon,
            "timestamp": int(1000 * self.timestamp),
            "body_temperature": self.body_temperature,
            "pulse_rate": self.pulse_rate,
            "deceased": self.deceased,
            "injury": self.injury,
            "injury_time": None
            if self.injury_time is None
            else int(1000 * self.injury_time),
        }

    def move(self) -> None:
        def _equation(
            M: float,
            m: float,
            T: float,
            t: float,
        ) -> float:
            #   ^
            #   |
            # M +\
            #   |\\\
            #   |\\\\\
            #   |\\\\\\\
            #   |\\\\\\\\\
            # m +---------+
            #   |         |
            #   +---------+----> (time)
            #   0         T
            return round(m + (M - m) * (T - t) / T, 2)

        timestamp = time.time()
        
        if not self.deceased:

            if self.injury is None:
                self.injury = random.choices(
                    list(self._injuries.keys()),
                    weights=self._injuries.values(),
                    k=1,
                )[0]
                if not self.injury is None:
                    self.injury_time = timestamp

            if not self.injury is None:

                _delta_injury_time = timestamp - self.injury_time
                _speed = self._config_injury.data[self.injury].moving_speed_kph / 3.6

                if _delta_injury_time == 0:
                    self.pulse_rate += self._config_injury.data[self.injury].pulse_rate_surge
                    self.body_temperature = max(
                        self.body_temperature
                        - self._config_injury.data[self.injury].body_temperature_drop,
                        self._config_general.deceased_if_body_temperature_under + 1,
                    )
                    self._T = self._config_injury.data[self.injury].death_minutes * 60
                    self._pulse_rate_M = float(self.pulse_rate)
                    self._pulse_rate_m = (
                        self._config_general.deceased_if_pulse_rate_under
                    )
                    self._body_temperature_M = float(self.body_temperature)
                    self._body_temperature_m = (
                        self._config_general.deceased_if_body_temperature_under
                    )

                else:
                    self.pulse_rate = _equation(
                        self._pulse_rate_M,
                        self._pulse_rate_m,
                        self._T,
                        _delta_injury_time,
                    )
                    self.body_temperature = _equation(
                        self._body_temperature_M,
                        self._body_temperature_m,
                        self._T,
                        _delta_injury_time,
                    )

            else:
                _speed = random.randint(
                    int(self._config_deployment.moving_speed_kph_min * 100),
                    int(self._config_deployment.moving_speed_kph_max * 100),
                ) / (3.6 * 100)

                self.pulse_rate = round(
                    max(
                        min(
                            self.pulse_rate
                            + random.randint(
                                -5,
                                5,
                            ),
                            self._config_general.normal_pulse_rate_max,
                        ),
                        self._config_general.normal_pulse_rate_min,
                    ),
                    2,
                )

            _delta_time = timestamp - self.timestamp
            distance = _speed * (_delta_time)
            self.current_location = self._coordinates.destination(
                self.current_location,
                self._bearing_angle,
                distance,
            )

            if self.pulse_rate <= self._config_general.deceased_if_pulse_rate_under:
                self.deceased = True
                self.pulse_rate = 0

        self.timestamp = timestamp