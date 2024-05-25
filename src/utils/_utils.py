import math
import random
import logging

from utils._basemodels import Coordinate


## Generic Functions
def format_timestamp(timestamp: float) -> int:
    return int(1000 * timestamp)


def sys_exc(exc_info) -> str:
    exc_type, exc_obj, exc_tb = exc_info
    return f"{exc_type} | {exc_tb.tb_lineno} | {exc_obj}"


def set_log_handler(id: str) -> str:
    logging.basicConfig(
        format=f"[{id}] %(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def rand_range_float(
    value_min: float,
    value_max: float,
) -> float:
    precision = 10000000
    return (
        random.randint(
            int(value_min * precision),
            int(value_max * precision),
        )
        / precision
    )


def random_gauss(
    value,
    mu,
    sigma,
    value_min,
    value_max,
) -> float:
    return min(
        max(
            value + random.gauss(mu, sigma),
            value_min,
        ),
        value_max,
    )


class Coordinates:
    # Earth radius in metres
    R = 6372797.6

    def destination(
        self,
        coordinate: Coordinate,
        bearing: float,
        distance: float,
    ) -> Coordinate:
        """
        Destination point given distance and bearing from start point
        Given a start point, initial bearing, and distance, this will calculate the destina­tion point and final bearing travelling along a (shortest distance) great circle arc.
        :arguments:
        - coordinate: Latitude and Longitude (Coordinate)
        - bearing: angle in degrees
        - distance: distance in meters
        :return:
        - Latitude and Longitude (Coordinate)
        """

        bearing_rad = bearing * math.pi / 180
        lat_rad = coordinate.lat * math.pi / 180
        lon_rad = coordinate.lon * math.pi / 180
        angular_distance = distance / Coordinates.R

        lat = math.asin(
            math.sin(lat_rad) * math.cos(angular_distance)
            + math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
        )

        lon = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat_rad),
            math.cos(angular_distance) - math.sin(lat_rad) * math.sin(lat),
        )

        return Coordinate(
            lat=round(lat * 180 / math.pi, 7),
            lon=round(lon * 180 / math.pi, 7),
        )
