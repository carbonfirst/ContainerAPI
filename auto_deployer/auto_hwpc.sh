#!/usr/bin/env bash

echo -n "Enter the sensor name: "
read sensor_name

echo "
{
    \"name\": \"${sensor_name}\",
    \"verbose\": true,
    \"frequency\": 1000,
    \"output\": {
      \"type\": \"mongodb\",
      \"uri\": \"mongodb://127.0.0.1\",
      \"database\": \"db_sensor\",
      \"collection\": \"report_0\"
    },
    \"system\": {
      \"rapl\": {
        \"events\": [\"RAPL_ENERGY_PKG\"],
        \"monitoring_type\": \"MONITOR_ONE_CPU_PER_SOCKET\"
      },
      \"msr\": {
        \"events\": [\"TSC\", \"APERF\", \"MPERF\"]
      }
    },
    \"container\": {
      \"core\": {
        \"events\": [
          \"CPU_CLK_THREAD_UNHALTED:REF_P\",
          \"CPU_CLK_THREAD_UNHALTED:THREAD_P\",
          \"LLC_MISSES\",
          \"INSTRUCTIONS_RETIRED\"
        ]
      }
    }
  }
" > ../config/hwpc_config_file.json