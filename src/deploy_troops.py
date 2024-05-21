import os
import time
import yaml
import queue
import logging

from dotenv import load_dotenv, find_dotenv
from threading import Thread

from utils.gps import Coordinate, Coordinates
from utils.troops import (
    Troop,
    ConfigTroopsGeneral,
    ConfigTroopsDeployment,
    ConfigTroopsRanks,
    ConfigTroopsBloodTypes,
    ConfigTroopsInjury,
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
    queue_troops = queue.Queue()
    queue_moves = queue.Queue()

    # Troops configuration
    troops_config_file = os.environ.get("TROOPS_CONFIG")
    logging.info(f"Loading troops configuration file: {troops_config_file}")
    with open(troops_config_file, "r") as f:
        troops_config = yaml.safe_load(f)
    troops_config_general = ConfigTroopsGeneral(**troops_config["general"])
    troops_config_deployment = ConfigTroopsDeployment(**troops_config["deployment"])
    troops_config_ranks = ConfigTroopsRanks(data=troops_config["ranks"])
    troops_config_blood_types = ConfigTroopsBloodTypes(
        data=troops_config["blood_types"]
    )
    troops_config_injures = ConfigTroopsInjury(data=troops_config["injures"])

    # Deploy troops
    start = Coordinate(
        lat=troops_config_deployment.start_latitude,
        lon=troops_config_deployment.start_longitude,
    )
    c = Coordinates()
    troops = list()
    for n in range(troops_config_deployment.number_of_troops):
        start = c.destination(
            start,
            90,
            troops_config_deployment.troops_distance_between,
        )
        troops.append(
            Troop(
                start,
                troops_config_general,
                troops_config_deployment,
                troops_config_blood_types,
                troops_config_ranks,
                troops_config_injures,
            )
        )
        queue_troops.put(troops[n].payload_non_transactional())
        logging.info(troops[n].payload_non_transactional())

    # Move troops around the battle field
    while True:
        for troop in troops:
            troop.move()
            queue_moves.put(troop.payload_transactional())
            logging.info(troop.payload_transactional())
        time.sleep(troops_config_deployment.seconds_between_moves)
