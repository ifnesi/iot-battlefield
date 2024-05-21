import os
import sys
import time
import yaml
import queue
import logging
from configparser import ConfigParser

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


def sys_exc(exc_info) -> str:
    exc_type, exc_obj, exc_tb = exc_info
    return f"{exc_type} | {exc_tb.tb_lineno} | {exc_obj}"


class Kafka:
    def __init__(
        self,
        target_lower: str,
        target_upper: str,
    ) -> None:
        # Kafka config
        kafka_config = os.environ["KAFKA_CONFIG"]
        kafka_client_id = os.environ[f"{target_upper}_KAFKA_CLIENT_ID"]
        self.kafka_topic = os.environ[f"{target_upper}_KAFKA_TOPIC"]
        self.kafka_topic_move = os.environ[f"{target_upper}_MOVE_KAFKA_TOPIC"]

        config = ConfigParser()
        config.read(kafka_config)

        # Producer
        kafka_config = dict(config["kafka"])
        kafka_config["client.id"] = kafka_client_id
        self.producer = Producer(kafka_config)

        # Schema Registry
        schema_registry_config = dict(config["schema-registry"])
        schema_registry_client = SchemaRegistryClient(schema_registry_config)
        self.string_serializer = StringSerializer("utf_8")
        with open(os.path.join("schemas", f"{target_lower}.avro"), "r") as f:
            self.avro_serializer = AvroSerializer(
                schema_registry_client,
                schema_str=f.read(),
            )
        with open(os.path.join("schemas", f"{target_lower}_move.avro"), "r") as f:
            self.avro_serializer_move = AvroSerializer(
                schema_registry_client,
                schema_str=f.read(),
            )

        # Data queues
        self.queue_data = queue.Queue()
        self.queue_moves = queue.Queue()

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
        while True:
            try:
                payload = None
                if not self.queue_data.empty():
                    payload = self.queue_data.get()
                    topic = self.kafka_topic
                    serialiser = self.avro_serializer
                    self.queue_data.task_done()
                elif not self.queue_moves.empty():
                    payload = self.queue_moves.get()
                    topic = self.kafka_topic_move
                    serialiser = self.avro_serializer_move
                    self.queue_moves.task_done()

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

                time.sleep(0.01)

            except Exception:
                logging.error(sys_exc(sys.exc_info()))

            except KeyboardInterrupt:
                logging.info("CTRL-C pressed by user")
                break

        logging.info("Flushing Kafka Producer")
        self.producer.flush()

def deploy(
    target: str,
):
    target_lower = target.lower()
    target_upper = target.upper()

    # Screen log handler
    logging.basicConfig(
        format=f"[{target_lower}] %(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Load env variables
    load_dotenv(find_dotenv())

    kafka = Kafka(
        target_lower,
        target_upper,
    )

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

    # Deploy
    start = Coordinate(
        lat=config_deployment.start_latitude,
        lon=config_deployment.start_longitude,
    )
    c = Coordinates()
    units = list()
    for n in range(config_deployment.number_of_units):
        try:
            start = c.destination(
                start,
                90,
                config_deployment.distance_between_units,
            )
            params["start_point"] = start
            units.append(class_to_call(**params))
            kafka.queue_data.put(units[n].payload_non_transactional())
            logging.info(units[n].payload_non_transactional())

        except Exception:
            logging.error(sys_exc(sys.exc_info()))

    # Start thread to process queues
    Thread(
        target=kafka.process_queues,
    ).start()

    # Move units around the battle field (main thread)
    while True:
        for unit in units:
            try:
                unit.move()
                kafka.queue_moves.put(unit.payload_transactional())
                logging.info(unit.payload_transactional())

            except Exception:
                logging.error(sys_exc(sys.exc_info()))

        time.sleep(config_deployment.seconds_between_moves)
