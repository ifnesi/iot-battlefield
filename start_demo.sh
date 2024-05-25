#!/bin/bash

function logging() {
  TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S.000"`
  LEVEL=${2-"INFO"}
  if [[ $3 == "-n" ]]; then
    echo -n "[start_demo] $TIMESTAMP [$LEVEL]: $1"
  else
    echo "[start_demo] $TIMESTAMP [$LEVEL]: $1"
  fi
}

logging "Loading environment variables"

logging "Starting docker compose"
if ! docker compose up -d --build ; then
    logging "Please start Docker Desktop!" "ERROR"
    exit -1
fi

# Waiting services to be ready
logging "Waiting Schema Registry to be ready" "INFO" -n
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' http://localhost:8081)" != "200" ]]
do
    echo -n "."
    sleep 1
done

echo ""
logging "Waiting ksqlDB Cluster to be ready" "INFO" -n
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' http://localhost:8088/info)" != "200" ]]
do
    echo -n "."
    sleep 1
done

echo ""
logging "Waiting Connect Cluster to be ready" "INFO" -n
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' http://localhost:8083)" != "200" ]]
do
    echo -n "."
    sleep 1
done

echo ""
logging "Waiting Confluent Control Center to be ready" "INFO" -n
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' http://localhost:9021)" != "200" ]]
do
    echo -n "."
    sleep 1
done

# Open browser with C3 and PGAdmin consoles
python3 -m webbrowser -t "http://localhost:5050"
python3 -m webbrowser -t "http://localhost:9021/clusters"

logging "Demo successfully started"

echo ""