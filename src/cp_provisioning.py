import os
import re
import glob
import json
import time
import yaml
import logging
import requests

from dotenv import load_dotenv, find_dotenv
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema


def flat_file(
    file: str,
) -> str:
    with open(file, "r") as f:
        data = " ".join([line.strip("\n").strip(" ") for line in f.readlines()])
    return data


def repl_env_vars(
    text: str,
    yaml_config: dict,
) -> str:
    # Replace Env vars
    env_vars = set(re.findall("\$([A-Za-z-_]+)", text))
    for var in env_vars:
        if var in os.environ.keys():
            text = text.replace(f"${var}", os.environ[var])
    # Replace YAML config
    for key in yaml_config.keys():
        if f"${key}" in text:
            text = text.replace(f"${key}", yaml_config[key])
    return text


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

    # Load YAML config
    yaml_config = dict()
    for target in ["TROOPS", "TANKS", "BASES", "FLC"]:
        config_file = os.environ.get(f"{target}_CONFIG")
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            # Flat YAML config out
            for k1, v1 in config.items():
                for k2, v2 in v1.items():
                    yaml_config[f"{target}.{k1}.{k2}"] = v2

    # Create Topics/Schemas
    topics = {
        yaml_config["BASES.kafka.topic_data"]: os.path.join(
            "schemas",
            "bases.avro",
        ),
        yaml_config["TROOPS.kafka.topic_data"]: os.path.join(
            "schemas",
            "troops.avro",
        ),
        yaml_config["TROOPS.kafka.topic_move"]: os.path.join(
            "schemas", "troops_move.avro"
        ),
        yaml_config["TANKS.kafka.topic_data"]: os.path.join(
            "schemas",
            "tanks.avro",
        ),
        yaml_config["TANKS.kafka.topic_move"]: os.path.join(
            "schemas",
            "tanks_move.avro",
        ),
        yaml_config["FLC.kafka.topic_data"]: os.path.join(
            "schemas",
            "flc.avro",
        ),
        yaml_config["FLC.kafka.topic_move"]: os.path.join(
            "schemas",
            "flc_move.avro",
        ),
    }

    kafka_config_file = os.environ.get("KAFKA_CONFIG")
    with open(kafka_config_file, "r") as f:
        kafka_config = yaml.safe_load(f)

    kafka_admin = AdminClient(dict(kafka_config["kafka"]))
    schema_registry_client = SchemaRegistryClient(dict(kafka_config["schema-registry"]))

    for topic, schema_file in topics.items():
        # Create topic
        logging.info(f"Creating topic: {topic}")
        kafka_admin.create_topics([NewTopic(topic, 1, 1)])
        # Create schema
        schema_subject = f"{topic}-value"
        logging.info(f"Creating schema subject: {schema_subject}")
        with open(schema_file, "r") as f:
            schema_str = f.read()
            schema_registry_client.register_schema(
                schema_subject,
                Schema(schema_str, "AVRO"),
            )
        # Wait for topic to be created
        while True:
            topics_list = kafka_admin.list_topics().topics
            if topic in topics_list.keys():
                break

    # ksqlDB
    logging.info("Submitting ksqlDB statements\n")
    for file in sorted(glob.glob(os.path.join("ksqldb", "*.sql"))):
        statement = repl_env_vars(flat_file(file), yaml_config)
        logging.info(f"{file}:\n{statement}")
        try:
            response = requests.post(
                "http://ksqldb-server:8088/ksql",
                headers={
                    "Content-Type": "application/vnd.ksql.v1+json; charset=utf-8",
                },
                json={
                    "ksql": statement,
                    "streamsProperties": {
                        "ksql.streams.auto.offset.reset": "earliest",
                        "ksql.streams.cache.max.bytes.buffering": "0",
                    },
                },
            )

            if response.status_code == 200:
                log = logging.info
                status_code = response.status_code
                response = json.dumps(response.json(), indent=3)
            else:
                log = logging.error
                status_code = response.status_code
                response = json.dumps(response.json(), indent=3)

        except Exception as err:
            log = logging.critical
            status_code = "50X"
            response = err

        finally:
            log(f"Response [Status Code = {status_code}]:\n{response}\n")

        time.sleep(1)

    # Connectors
    for connector_config_file in glob.glob(os.path.join("connectors", "*.json")):
        connector_name = os.path.splitext(os.path.split(connector_config_file)[-1])[0]
        logging.info(f"Creating connector: {connector_name}")
        with open(connector_config_file, "r") as f:
            try:
                # Create connector
                response = requests.put(
                    f"http://connect-1:8083/connectors/{connector_name}/config",
                    headers={
                        "Content-Type": "application/json",
                    },
                    json=json.loads(repl_env_vars(f.read(), yaml_config)),
                )

                if response.status_code == 200:
                    log = logging.info
                    status_code = response.status_code
                    response = json.dumps(response.json(), indent=3)
                else:
                    log = logging.error
                    status_code = response.status_code
                    response = json.dumps(response.json(), indent=3)

            except Exception as err:
                log = logging.critical
                status_code = "50X"
                response = err

            finally:
                log(f"Response [Status Code = {status_code}]:\n{response}\n")

            time.sleep(5)

            # Check connector status
            response = requests.get(
                f"http://connect-1:8083/connectors/{connector_name}/status"
            )
            logging.info(json.dumps(response.json(), indent=3))
            time.sleep(3)
