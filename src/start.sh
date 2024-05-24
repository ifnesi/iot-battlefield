#!/bin/bash

set -m
source .env

function logging() {
  TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S.000"`
  LEVEL=${2-"INFO"}
  if [[ $3 == "-n" ]]; then
    echo -n "$TIMESTAMP [$LEVEL]: $1"
  else
    echo "$TIMESTAMP [$LEVEL]: $1"
  fi
}

# Waiting services to be ready
logging "Waiting Schema Registry to be ready" "INFO" -n
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' http://schema-registry:8081)" != "200" ]]
do
    echo -n "."
    sleep 1
done
sleep 1

echo ""
logging "Waiting ksqlDB Cluster to be ready" "INFO" -n
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' http://ksqldb-server:8088/info)" != "200" ]]
do
    echo -n "."
    sleep 1
done

echo ""
logging "Waiting Connect Cluster to be ready" "INFO" -n
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' http://connect-1:8083)" != "200" ]]
do
    echo -n "."
    sleep 1
done

echo ""
logging "Waiting Confluent Control Center to be ready" "INFO" -n
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' http://control-center:9021)" != "200" ]]
do
    echo -n "."
    sleep 1
done
sleep 1

# Create topics, ksqlDB tables/streams and connectors
sleep 3
exec python cp_provisioning.py &

# Start emulator
sleep 60
exec python deployment.py --target=bases &
exec python deployment.py --target=tanks &
exec python deployment.py --target=troops &
exec python deployment.py --target=flc
