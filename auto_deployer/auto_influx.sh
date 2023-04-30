#!/usr/bin/env bash
#docker run -d --name influxdb -p 8086:8086 influxdb

echo "Complete influx setup and configure smartwatts config file"

# docker exec -it influxdb influx setup \
#   --username admin \
#   --password admin123 \
#   --org umass \
#   --bucket power_consumption \
#   --force

VAR=$(docker exec -it influxdb influx auth list --json)

TOKEN=$(echo $VAR | grep -o '"token": "[^"]*'| grep -o '[^"]*$') 

echo $TOKEN > ../config/token.txt