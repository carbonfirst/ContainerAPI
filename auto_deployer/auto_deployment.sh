#!/usr/bin/env bash

echo "Instantiating mongodb"

./auto_mongo.sh

echo "Creating hwpc config file"

echo "Name of hwpc-sensor"

./auto_hwpc.sh

echo "Instantiating hwpc-sensor"

docker run -d --rm --name hwpc-sensor --net=host --privileged --pid=host -v /sys:/sys -v /var/lib/docker/containers:/var/lib/docker/containers:ro -v /tmp/powerapi-sensor-reporting:/reporting -v $(pwd):/srv -v $(pwd)/hwpc_config_file.json:/config_file.json powerapi/hwpc-sensor --config-file /config_file.json

echo "Instantiating influxdb"

./auto_influx.sh

echo "Creating smartwatts config file"

./auto_smartwatts.sh "$(<../config/token.txt)"

echo "Instantiating smartwatts-formula"

docker run -td --name smartwatts-formula --net=host -v $(pwd)/smartwatts_config_file.json:/config_file.json powerapi/smartwatts-formula --config-file /config_file.json
