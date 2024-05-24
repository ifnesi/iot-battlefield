import os
import sys
import time
import yaml
import queue
import logging

from dotenv import load_dotenv, find_dotenv
from threading import Thread

from confluent_kafka import Producer
from confluent_kafka.serialization import (
    StringSerializer,
    SerializationContext,
    MessageField,
)
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

from utils.gps import Coordinates
from utils.bases import Base
from utils.tanks import Tank
from utils.troops import Troop
from utils.flc import FLC
from utils.basemodels import (
    Coordinate,
    ConfigKafkaUnits,
    ConfigTanksDeployment,
    ConfigTanksModels,
    ConfigTroopsGeneral,
    ConfigTroopsDeployment,
    ConfigTroopsRanks,
    ConfigTroopsBloodTypes,
    ConfigTroopsInjury,
    ConfigBases,
    ConfigFLCDeployment,
)


def sys_exc(exc_info) -> str:
    exc_type, exc_obj, exc_tb = exc_info
    return f"{exc_type} | {exc_tb.tb_lineno} | {exc_obj}"


class Kafka:
    def __init__(
        self,
        target: str,
        kafka_config: dict,
        unit_config: ConfigKafkaUnits,
    ) -> None:
        # Producer
        kafka_config["kafka"]["client.id"] = unit_config.client_id
        self.producer = Producer(kafka_config["kafka"])
        self.topic_data = unit_config.topic_data
        self.topic_move = unit_config.topic_move
        self.stop_thread = False

        # Data queues
        self.queue_data = queue.Queue()
        self.queue_moves = queue.Queue()

        # Schema Registry
        schema_registry_config = dict(kafka_config["schema-registry"])
        schema_registry_client = SchemaRegistryClient(schema_registry_config)
        self.string_serializer = StringSerializer("utf_8")
        with open(os.path.join("schemas", f"{target}.avro"), "r") as f:
            self.avro_serializer = AvroSerializer(
                schema_registry_client,
                schema_str=f.read(),
            )
        moves_files = os.path.join("schemas", f"{target}_move.avro")
        if os.path.exists(moves_files):
            with open(moves_files, "r") as f:
                self.avro_serializer_move = AvroSerializer(
                    schema_registry_client,
                    schema_str=f.read(),
                )

    def delivery_report(
        self,
        err,
        msg,
    ) -> None:
        if isinstance(msg.key(), bytes):
            key = msg.key().decode("utf-8")
        else:
            key = msg.key()
        if err is not None:
            logging.error(
                f"Delivery failed for record/key '{key}' for the topic '{msg.topic()}': {err}"
            )

    def process_queues(self) -> None:
        exit_if_zero = 60
        while True:
            try:
                payload = None

                if not self.queue_data.empty():
                    payload = self.queue_data.get()
                    topic = self.topic_data
                    serialiser = self.avro_serializer
                elif not self.queue_moves.empty():
                    payload = self.queue_moves.get()
                    topic = self.topic_move
                    serialiser = self.avro_serializer_move
                else:
                    time.sleep(0.5)
                    if self.stop_thread:
                        exit_if_zero -= 1
                    if exit_if_zero == 0:
                        break

                if payload is not None:
                    self.producer.poll(0)
                    self.producer.produce(
                        topic=topic,
                        key=payload["id"],
                        value=serialiser(
                            payload,
                            SerializationContext(
                                topic,
                                MessageField.VALUE,
                            ),
                        ),
                        on_delivery=self.delivery_report,
                    )

            except Exception:
                logging.error(sys_exc(sys.exc_info()))

            except KeyboardInterrupt:
                logging.info("CTRL-C pressed by user")
                break

        logging.info("Flushing Kafka Producer")
        self.producer.flush()


def deploy_units(
    target: str,
    dry_run: bool,
):

    # Screen log handler
    logging.basicConfig(
        format=f"[{target}] %(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Load env variables
    load_dotenv(find_dotenv())

    # Configuration
    config_file = os.environ.get(f"{target.upper()}_CONFIG")
    logging.info(f"Loading {target} configuration file: {config_file}")
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    if target == "tanks":
        config_deployment = ConfigTanksDeployment(**config["deployment"])
        config_models = ConfigTanksModels(data=config["models"])
        class_to_call = Tank
        params = {
            "start_point": None,
            "config_deployment": config_deployment,
            "config_models": config_models,
        }

    elif target == "troops":
        config_general = ConfigTroopsGeneral(**config["general"])
        config_deployment = ConfigTroopsDeployment(**config["deployment"])
        config_ranks = ConfigTroopsRanks(data=config["ranks"])
        config_blood_types = ConfigTroopsBloodTypes(data=config["blood_types"])
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

    elif target == "bases":
        config_bases = ConfigBases(data=config["bases"])

    elif target == "flc":
        config_lfc = ConfigFLCDeployment(**config["deployment"])

    else:
        raise Exception(f"Invalid target '{target}'")

    # Kafka
    if not dry_run:
        kafka_config_file = os.environ.get("KAFKA_CONFIG")
        with open(kafka_config_file, "r") as f:
            kafka_config = yaml.safe_load(f)
        kafka = Kafka(
            target,
            kafka_config,
            ConfigKafkaUnits(**config["kafka"]),
        )

        # Start thread to process queues
        kafka_thread = Thread(
            target=kafka.process_queues,
        )
        kafka_thread.start()

    # Deploy units/bases
    if target == "bases":
        for base_id, config_base in config_bases.data.items():
            try:
                base = Base(
                    base_id,
                    config_base,
                )
                payload = base.payload_non_transactional()
                logging.info(payload)
                if not dry_run:
                    kafka.queue_data.put(payload)
            except Exception:
                logging.error(sys_exc(sys.exc_info()))

    elif target == "flc":
        lfcs = list()
        for location, config in config_lfc.locations.items():
            try:
                lfc = FLC(
                    location,
                    config,
                    config_lfc.seconds_between_moves,
                )
                lfcs.append(lfc)
                payload = lfc.payload_non_transactional()
                logging.info(payload)
                if not dry_run:
                    kafka.queue_data.put(payload)
            except Exception:
                logging.error(sys_exc(sys.exc_info()))

        # Emulate supply levels (main thread)
        while True:
            for lfc in lfcs:
                try:
                    lfc.move()
                    payload = lfc.payload_transactional()
                    logging.info(payload)
                    if not dry_run:
                        kafka.queue_moves.put(payload)

                except Exception:
                    logging.error(sys_exc(sys.exc_info()))

            time.sleep(lfc._seconds_between_moves)

    else:  # troops / tanks
        c = Coordinates()
        start = Coordinate(
            lat=config_deployment.start_latitude,
            lon=config_deployment.start_longitude,
        )
        units = list()
        stop_reporting = dict()
        for n in range(config_deployment.number_of_units):
            try:
                start = c.destination(
                    start,
                    config_deployment.bearing_angle_between_units,
                    config_deployment.distance_between_units,
                )
                params["start_point"] = start
                units.append(class_to_call(**params))
                payload = units[n].payload_non_transactional()
                logging.info(payload)
                if not dry_run:
                    stop_reporting[payload["id"]] = False
                    kafka.queue_data.put(payload)

            except Exception:
                logging.error(sys_exc(sys.exc_info()))

        # Move units around the battle field (main thread)
        while True:
            for unit in units:
                try:
                    unit.move()
                    payload = unit.payload_transactional()
                    if not stop_reporting[payload["id"]]:
                        logging.info(payload)
                        if not dry_run:
                            kafka.queue_moves.put(payload)
                            stop_reporting[payload["id"]] = payload.get(
                                "deceased", False
                            ) or payload.get("destroyed", False)

                except Exception:
                    logging.error(sys_exc(sys.exc_info()))

            time.sleep(config_deployment.seconds_between_moves)

    if not dry_run:
        logging.info("Waiting Kafka thread to finish")
        kafka.stop_thread = True
        kafka_thread.join()
        logging.info("Kafka thread finished")
