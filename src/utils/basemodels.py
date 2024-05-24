from typing import Dict
from pydantic import BaseModel, field_validator


class Coordinate(BaseModel):
    lat: float
    lon: float


class ConfigKafkaUnits(BaseModel):
    client_id: str
    topic_data: str
    topic_move: str


class ConfigTanksDeployment(BaseModel):
    number_of_units: int
    start_latitude: float
    start_longitude: float
    bearing_angle_min: float
    bearing_angle_max: float
    distance_between_units: float
    bearing_angle_between_units: float
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


class ConfigBasesBase(BaseModel):
    name: str
    type: str
    latitude: float
    longitude: float


class ConfigBases(BaseModel):
    data: Dict[str, ConfigBasesBase]


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
    number_of_units: int
    start_latitude: float
    start_longitude: float
    bearing_angle_min: int
    bearing_angle_max: int
    moving_speed_kph_min: float
    moving_speed_kph_max: float
    distance_between_units: float
    bearing_angle_between_units: float
    seconds_between_moves: float
    ammunition_min: int
    ammunition_max: int
    ammunition_rps_min: float
    ammunition_rps_max: float


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
    able_to_use_ammo: bool


class ConfigTroopsInjury(BaseModel):
    data: Dict[str, ConfigTroopsInjuryBase]

    @field_validator("data")
    def add_no_injury(cls, data):
        sum_prob = sum([value.probability for value in data.values()])
        data[None] = ConfigTroopsInjuryBase(
            probability=(100 - sum_prob) if sum_prob < 100 else 50 * sum_prob,
            death_minutes=0,
            pulse_rate_surge=0,
            body_temperature_drop=0,
            moving_speed_kph=0,
            able_to_use_ammo=True,
        )
        return data


class ConfigFLCDeploymentBase(BaseModel):
    latitude: float
    longitude: float
    food_level_min: float
    food_level_max: float
    food_level_var_min: float
    food_level_var_max: float
    ammunition_level_min: float
    ammunition_level_max: float
    ammunition_level_var_min: float
    ammunition_level_var_max: float
    health_level_min: float
    health_level_max: float
    health_level_var_min: float
    health_level_var_max: float


class ConfigFLCDeployment(BaseModel):
    seconds_between_moves: float
    locations: Dict[str, ConfigFLCDeploymentBase]
