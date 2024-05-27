import time
import random
import hashlib

from faker import Faker

from utils._utils import rand_range_float, random_gauss, format_timestamp, Coordinates
from utils._basemodels import (
    Coordinate,
    ConfigTroopsGeneral,
    ConfigTroopsDeployment,
    ConfigTroopsBloodTypes,
    ConfigTroopsRanks,
    ConfigTroopsInjury,
)


class Troop:
    def __init__(
        self,
        unit: str = None,
        start_point: Coordinate = None,
        config_general: ConfigTroopsGeneral = None,
        config_deployment: ConfigTroopsDeployment = None,
        config_blood_types: ConfigTroopsBloodTypes = None,
        config_ranks: ConfigTroopsRanks = None,
        config_injury: ConfigTroopsInjury = None,
    ) -> None:
        self.timestamp = time.time()
        self.health = 100
        self.deceased = False
        self.injury = None
        self.injury_time = None
        self.unit = unit
        self.current_location = start_point
        self._ammo_shot = 0
        self._coordinates = Coordinates()
        self._config_general = config_general
        self._config_deployment = config_deployment
        self._config_injury = config_injury
        self._injuries = {
            injury: data.probability for injury, data in config_injury.data.items()
        }

        f = Faker()
        self.name = f.name()

        self.height = random_gauss(
            0,
            config_general.height_mean,
            config_general.height_stdev,
            value_min=150,
            value_max=215,
        )

        bmi = random_gauss(
            0,
            config_general.bmi_mean,
            config_general.bmi_stdev,
            value_min=18,
            value_max=32,
        )
        self.weight = bmi * (self.height / 100) ** 2

        self.ammo = random_gauss(
            0,
            config_deployment.ammunition_mean,
            config_deployment.ammunition_stdev,
            value_min=50,
        )

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

        self.id = f"troop_{hashlib.sha256(f'{self.unit}_{self.name}_{self.rank}_{self.blood_type}'.encode('utf-8')).hexdigest()[:12]}"

        self.body_temperature = rand_range_float(
            config_general.normal_body_temperature_min,
            config_general.normal_body_temperature_max,
        )

        self.pulse_rate = rand_range_float(
            config_general.normal_pulse_rate_min,
            config_general.normal_pulse_rate_max,
        )

        self._bearing_angle = random_gauss(
            0,
            config_deployment.bearing_angle_mean,
            config_deployment.bearing_angle_stdev,
            value_min=-360,
            value_max=360,
        )

    def payload_non_transactional(self) -> dict:
        return {
            "id": self.id,
            "unit": self.unit,
            "name": self.name,
            "height": int(self.height),
            "weight": round(self.weight, 2),
            "blood_type": self.blood_type,
            "rank": self.rank,
            "timestamp": format_timestamp(self.timestamp),
        }

    def payload_transactional(self) -> dict:
        return {
            "id": self.id,
            "lat": self.current_location.lat,
            "lon": self.current_location.lon,
            "body_temperature": round(self.body_temperature, 2),
            "pulse_rate": int(self.pulse_rate),
            "ammo": int(max(self.ammo - self._ammo_shot, 0)),
            "health": self.health,
            "injury": self.injury,
            "injury_time": None
            if self.injury_time is None
            else format_timestamp(self.injury_time),
            "deceased": self.deceased,
            "timestamp": format_timestamp(self.timestamp),
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
            #   |    |    |
            #   +----+----+----> (time)
            #   0    t    T
            return round(m + (M - m) * (T - t) / T, 2)

        timestamp = time.time()

        if not self.deceased:

            _delta_time = timestamp - self.timestamp

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
                    self.pulse_rate += self._config_injury.data[
                        self.injury
                    ].pulse_rate_surge
                    self.body_temperature = max(
                        self.body_temperature
                        - self._config_injury.data[self.injury].body_temperature_drop,
                        self._config_general.deceased_if_body_temperature_under + 1,
                    )
                    self._T = random_gauss(
                        0,
                        self._config_injury.data[self.injury].death_minutes_mean,
                        self._config_injury.data[self.injury].death_minutes_stdev,
                        value_min=0,
                      )  * 60
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

                self.health = int(
                    max(
                        _equation(
                            100,
                            0,
                            self._T,
                            _delta_injury_time,
                        ),
                        0,
                    )
                )

            else:
                _speed = (
                    random_gauss(
                        0,
                        self._config_deployment.moving_speed_kph_mean,
                        self._config_deployment.moving_speed_kph_stdev,
                        value_min=0,
                    )
                    / 3.6
                )

                self.pulse_rate = random_gauss(
                    self.pulse_rate,
                    self._config_general.normal_pulse_rate_var_mean,
                    self._config_general.normal_pulse_rate_var_stdev,
                    value_min=self._config_general.normal_pulse_rate_min,
                    value_max=self._config_general.normal_pulse_rate_max,
                )

            if self._config_injury.data[self.injury].able_to_use_weapon:
                _rps = random_gauss(
                    0,
                    self._config_deployment.ammunition_rps_mean,
                    self._config_deployment.ammunition_rps_stdev,
                    value_min=0,
                )
                if self._ammo_shot < self.ammo:
                    self._ammo_shot += _rps * _delta_time

            distance = _speed * (_delta_time)
            self.current_location = self._coordinates.destination(
                self.current_location,
                self._bearing_angle,
                distance,
            )

            if self.pulse_rate <= self._config_general.deceased_if_pulse_rate_under:
                self.deceased = True
                self.pulse_rate = 0
                self.health = 0
                self.body_temperature = self._config_general.deceased_if_body_temperature_under

        self.timestamp = timestamp
