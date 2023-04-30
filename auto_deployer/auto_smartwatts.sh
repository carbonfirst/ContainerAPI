#!/usr/bin/env bash

maxfrequency=$(lscpu -b -p=MAXMHZ | tail -n -1| cut -d , -f 1)
minfrequency=$(lscpu -b -p=MINMHZ | tail -n -1 | cut -d , -f 1)
basefrequency=$(lscpu | grep "Model name" | cut -d @ -f 2 | cut -d G -f 1)
basefrequency=$(expr ${basefrequency}\*1000 | bc | cut -d . -f 1)
maxfrequency=$( printf "%.0f" $maxfrequency )
minfrequency=$( printf "%.0f" $minfrequency )

echo "
{
  \"verbose\": true,
  \"stream\": true,
  \"input\": {
    \"puller\": {
      \"model\": \"HWPCReport\",
      \"type\": \"mongodb\",
      \"uri\": \"mongodb:://127.0.0.1\",
      \"db\": \"db_sensor\",
      \"collection\": \"report_0\"
    }
  },
  \"output\": {
    \"pusher_power\": {
      \"type\": \"influxdb2\",
      \"uri\": \"127.0.0.1\",
      \"port\": 8086,
      \"name\": \"influx2_output\",
      \"db\" : \"power_consumption\",
      \"bucket\": \"power_consumption\",
      \"org\": \"umass\",
      \"token\": \"$1\"
    }
  },
  \"cpu-frequency-base\": $basefrequency,
  \"cpu-frequency-min\": $minfrequency,
  \"cpu-frequency-max\": $maxfrequency,
  \"cpu-error-threshold\": 2.0,
  \"disable-dram-formula\": true,
  \"sensor-report-sampling-interval\": 1000
}
" > ../config/smartwatts_config_file.json