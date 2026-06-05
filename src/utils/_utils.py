"""
Utility Functions Module

Provides helper functions for:
- Timestamp formatting
- Random number generation with constraints
- Geographic coordinate calculations
- Logging configuration
"""
import math
import random
import logging

from utils._basemodels import Coordinate


## Generic Functions
def format_timestamp(timestamp: float) -> int:
    """Convert Unix timestamp to milliseconds."""
    return int(1000 * timestamp)


def sys_exc(exc_info) -> str:
    """Format exception information for logging."""
    exc_type, exc_obj, exc_tb = exc_info
    return f"{exc_type} | {exc_tb.tb_lineno} | {exc_obj}"


def set_log_handler(id: str) -> None:
    """Configure logging with a specific identifier prefix."""
    logging.basicConfig(
        format=f"[{id}] %(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def rand_range_float(
    value_min: float,
    value_max: float,
) -> float:
    """Generate a random float between min and max with high precision."""
    precision = 10000000
    return (
        random.randint(
            int(value_min * precision),
            int(value_max * precision),
        )
        / precision
    )


def random_gauss(
    value: float,
    mu: float,
    sigma: float,
    value_min: float = None,
    value_max: float = None,
) -> float:
    """
    Generate a new value using Gaussian distribution with optional bounds.
    
    Args:
        value: Current value
        mu: Mean of the Gaussian distribution
        sigma: Standard deviation
        value_min: Minimum allowed value (optional)
        value_max: Maximum allowed value (optional)
    
    Returns:
        New value within specified bounds
    """
    new_value = value + random.gauss(mu, sigma)
    if value_min is not None:
        new_value = max(new_value, value_min)
    if value_max is not None:
        new_value = min(new_value, value_max)
    return new_value


class Coordinates:
    """
    Geographic coordinate calculations using great circle distance.
    
    Provides methods to calculate destination points given a starting point,
    bearing angle, and distance.
    """
    # Earth radius in metres
    R = 6372797.6

    def destination(
        self,
        coordinate: Coordinate,
        bearing: float,
        distance: float,
    ) -> Coordinate:
        """
        Calculate destination point given distance and bearing from start point.
        
        Uses great circle arc calculations for accurate geographic positioning.
        
        Args:
            coordinate: Starting latitude and longitude
            bearing: Bearing angle in degrees (0-360, clockwise from north)
            distance: Distance to travel in meters
        
        Returns:
            Destination coordinate (lat, lon)
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
