import math

from pydantic import BaseModel


class Coordinate(BaseModel):
    lat: float
    lon: float


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
            lat=round(lat * 180 / math.pi, 8),
            lon=round(lon * 180 / math.pi, 8),
        )
