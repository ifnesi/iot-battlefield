import os
import time
import yaml
import queue
import logging

from dotenv import load_dotenv, find_dotenv
from threading import Thread

from utils.gps import Coordinate, Coordinates
from utils.tanks import (
    Tank,
    ConfigTanksDeployment,
    ConfigTanksModels,
)


if __name__ == "__main__":
    FILE_APP = os.path.splitext(os.path.split(__file__)[-1])[0]

    # Screen log handler
    logging.basicConfig(
        format=f"[{FILE_APP}] %(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Load env variables
    load_dotenv(find_dotenv())

    # Data queues
    queue_tanks = queue.Queue()
    queue_moves = queue.Queue()

    # Tanks configuration
    tanks_config_file = os.environ.get("TANKS_CONFIG")
    logging.info(f"Loading tanks configuration file: {tanks_config_file}")
    with open(tanks_config_file, "r") as f:
        tanks_config = yaml.safe_load(f)
    tanks_config_deployment = ConfigTanksDeployment(**tanks_config["deployment"])
    tanks_config_models = ConfigTanksModels(data=tanks_config["models"])

    # Deploy tanks
    start = Coordinate(
        lat=tanks_config_deployment.start_latitude,
        lon=tanks_config_deployment.start_longitude,
    )
    c = Coordinates()
    tanks = list()
    for n in range(tanks_config_deployment.number_of_tanks):
        start = c.destination(
            start,
            90,
            tanks_config_deployment.tanks_distance_between,
        )
        tanks.append(
            Tank(
                start,
                tanks_config_deployment,
                tanks_config_models,
            )
        )
        queue_tanks.put(tanks[n].payload_non_transactional())
        logging.info(tanks[n].payload_non_transactional())

    # Move troops around the battle field
    while True:
        for tank in tanks:
            tank.move()
            queue_moves.put(tank.payload_transactional())
            logging.info(tank.payload_transactional())
        time.sleep(tanks_config_deployment.seconds_between_moves)
