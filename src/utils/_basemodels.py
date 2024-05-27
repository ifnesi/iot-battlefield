from typing import Dict
from pydantic import BaseModel, field_validator


class Coordinate(BaseModel):
    lat: float
    lon: float


class ConfigKafkaUnits(BaseModel):
    client_id: str
    topic_data: str
    topic_move: str


class ConfigTanksDeploymentBase(BaseModel):
    number_of_units: int
    start_latitude: float
    start_longitude: float
    bearing_angle_mean: float
    bearing_angle_stdev: float
    distance_between_units: float
    bearing_angle_between_units: float
    damage_probability_mean: float
    damage_probability_stdev: float
    damage_impact_mean: float
    damage_impact_stdev: float


class ConfigTanksDeployment(BaseModel):
    seconds_between_moves: float
    units: Dict[str, ConfigTanksDeploymentBase]


class ConfigTanksModelsBase(BaseModel):
    proportion: float
    moving_speed_kph_mean: float
    moving_speed_kph_stdev: float
    ammunition_mean: float
    ammunition_stdev: float
    ammunition_rpm_mean: float
    ammunition_rpm_stdev: float
    damage_can_support_mean: float
    damage_can_support_stdev: float


class ConfigTanksModels(BaseModel):
    data: Dict[str, ConfigTanksModelsBase]


class ConfigTroopsGeneral(BaseModel):
    normal_pulse_rate_min: int
    normal_pulse_rate_max: int
    normal_pulse_rate_var_mean: int
    normal_pulse_rate_var_stdev: int
    normal_body_temperature_min: float
    normal_body_temperature_max: float
    bmi_mean: float
    bmi_stdev: float
    height_mean: float
    height_stdev: float
    deceased_if_pulse_rate_under: float
    deceased_if_body_temperature_under: float


class ConfigTroopsDeploymentBase(BaseModel):
    number_of_units: int
    start_latitude: float
    start_longitude: float
    bearing_angle_mean: float
    bearing_angle_stdev: float
    moving_speed_kph_mean: float
    moving_speed_kph_stdev: float
    distance_between_units: float
    bearing_angle_between_units: float
    ammunition_mean: float
    ammunition_stdev: float
    ammunition_rps_mean: float
    ammunition_rps_stdev: float


class ConfigTroopsDeployment(BaseModel):
    seconds_between_moves: float
    units: Dict[str, ConfigTroopsDeploymentBase]


class ConfigTroopsBloodTypes(BaseModel):
    data: Dict[str, float]


class ConfigTroopsRanks(BaseModel):
    data: Dict[str, float]


class ConfigTroopsInjuryBase(BaseModel):
    probability: float
    death_minutes_mean: float
    death_minutes_stdev: float
    pulse_rate_surge: float
    body_temperature_drop: float
    moving_speed_kph: float
    able_to_use_weapon: bool


class ConfigTroopsInjury(BaseModel):
    data: Dict[str, ConfigTroopsInjuryBase]

    @field_validator("data")
    def add_no_injury(cls, data):
        sum_prob = sum([value.probability for value in data.values()])
        data[None] = ConfigTroopsInjuryBase(
            probability=(100 - sum_prob) if sum_prob < 100 else 50 * sum_prob,
            death_minutes_mean=0,
            death_minutes_stdev=0,
            pulse_rate_surge=0,
            body_temperature_drop=0,
            moving_speed_kph=0,
            able_to_use_weapon=True,
        )
        return data


class ConfigFLCDeploymentBase(BaseModel):
    latitude: float
    longitude: float
    food_level_min: float
    food_level_max: float
    food_level_var_mean: float
    food_level_var_stdev: float
    ammunition_level_min: float
    ammunition_level_max: float
    ammunition_level_var_mean: float
    ammunition_level_var_stdev: float
    health_level_min: float
    health_level_max: float
    health_level_var_mean: float
    health_level_var_stdev: float


class ConfigFLCDeployment(BaseModel):
    seconds_between_moves: float
    locations: Dict[str, ConfigFLCDeploymentBase]
