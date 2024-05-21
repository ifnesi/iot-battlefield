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
from utils.troops import (
    Troop,
    ConfigTroopsGeneral,
    ConfigTroopsDeployment,
    ConfigTroopsRanks,
    ConfigTroopsBloodTypes,
    ConfigTroopsInjury,
)


def deploy(
    file_app: str,
    target: str,
):
    # Screen log handler
    logging.basicConfig(
        format=f"[{file_app}] %(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    target_lower = target.lower()
    target_upper = target.upper()

    # Load env variables
    load_dotenv(find_dotenv())

    # Data queues
    queue_data = queue.Queue()
    queue_moves = queue.Queue()

    # Configuration
    config_file = os.environ.get(f"{target_upper}_CONFIG")
    logging.info(f"Loading {target_lower} configuration file: {config_file}")
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    if target_lower == "tanks":
        config_deployment = ConfigTanksDeployment(**config["deployment"])
        config_models = ConfigTanksModels(data=config["models"])
        class_to_call = Tank
        params = {
            "start_point": None,
            "config_deployment": config_deployment,
            "config_models": config_models,
        }
    else:
        config_general = ConfigTroopsGeneral(**config["general"])
        config_deployment = ConfigTroopsDeployment(**config["deployment"])
        config_ranks = ConfigTroopsRanks(data=config["ranks"])
        config_blood_types = ConfigTroopsBloodTypes(
            data=config["blood_types"]
        )
        config_injury = ConfigTroopsInjury(data=config["injures"])
        class_to_call = Troop
        params = {
            "start_point": None,
            "config_general": config_general,
            "config_deployment": config_deployment,
            "config_blood_types": config_blood_types,
            "config_ranks": config_ranks,
            "config_injury": config_injury,
        }

    # Deploy
    start = Coordinate(
        lat=config_deployment.start_latitude,
        lon=config_deployment.start_longitude,
    )
    c = Coordinates()
    units = list()
    for n in range(config_deployment.number_of_units):
        start = c.destination(
            start,
            90,
            config_deployment.distance_between_units,
        )
        params["start_point"] = start
        units.append(
            class_to_call(**params)
        )
        queue_data.put(units[n].payload_non_transactional())
        logging.info(units[n].payload_non_transactional())

    # Move units around the battle field
    while True:
        for unit in units:
            unit.move()
            queue_moves.put(unit.payload_transactional())
            logging.info(unit.payload_transactional())
        time.sleep(config_deployment.seconds_between_moves)
