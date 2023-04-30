import yaml
import argparse
import datetime
import socket

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


def writeIdlePowerData(timestamp_column, idle_power_column):
    host_name = socket.gethostname()
    if(host_name != ""):
        sensor_name = host_name.split(".")[0]
    else:
        sensor_name = "obelix"
    print("The current sensor name is "+sensor_name)

    input_file_path = config["IDLE_POWER_DATA"]["FILE_PATH"]
    input_file_name = config["IDLE_POWER_DATA"]["FILE_NAME"]

    inputfile = open(input_file_path + "/" + input_file_name, 'r')
    print("input file " + input_file_name + " read at location " + input_file_path)

    datapoints = []
    lastKLines = 3
    with inputfile as csvfile:
        lines = csvfile.readlines()
        columns = lines[0].rstrip().split(',')

        timestampIndex = getColumnIndexInFile(columns, timestamp_column)
        if timestampIndex == -1:
            print("timestamp column not found in the idle power data file")
            exit

        idlePowerIndex = getColumnIndexInFile(columns, idle_power_column)
        if idlePowerIndex == -1:
            print("idle_power column not found in the idle power data file")
            exit

        for line in lines[max(-lastKLines, 1 - len(lines)):]:
            data = line.rstrip().split(',')

            unix_s = data[timestampIndex]

            timeDate = datetime.datetime.fromtimestamp(int(unix_s))

            point = Point(power_bucket).field("power", float(data[idlePowerIndex])).tag("sensor", sensor_name).tag("target", "idle_power").time(timeDate)
            print(point)

            datapoints.append(point)

        write_api.write(bucket = power_bucket, org = influx_org, record = datapoints)

        print('Done writing idle power values to influx')


def getColumnIndexInFile(columns, column_name):
    for index, column in enumerate(columns):
        if column == column_name:
            return index
    return -1

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Get the config file path from command line and optionally the column names in the idle power csv file')        # Parse the arguments from command prompt

    parser.add_argument("--config_file_path", "-config_path", required=False, type=str, default = "../config/config.yml")
    parser.add_argument("--timestamp_column", "-timestamp", required=False, type=str, default = "timestamp")
    parser.add_argument("--idle_power_column", "-idle_power", required=False, type=str, default = "idle_power")
    args = parser.parse_args()

    timestamp_column = args.timestamp_column
    idle_power_column = args.idle_power_column
    
    config_file_path = args.config_file_path
    with open(config_file_path, "r") as f:
        config = yaml.safe_load(f)

    HOST = config["INFLUX"]["HOST"]
    PORT = config["INFLUX"]["PORT"]
    influx_url = "http://" + HOST + ":" + PORT
    influx_token = config["INFLUX"]["TOKEN"]
    influx_org = config["INFLUX"]["ORG"]

    influx_client = InfluxDBClient(url = influx_url, token = influx_token, org = influx_org)
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    power_bucket = config["INFLUX"]["POWER_CONSUMPTION_BUCKET"]
    # Checking if bucket already exists
    bucket_api = influx_client.buckets_api()
    # If we can't find the bucket, we create it
    if bucket_api.find_bucket_by_name(power_bucket) is None:
        bucket_api.create_bucket(bucket_name = power_bucket, org_id = influx_org)

    writeIdlePowerData(timestamp_column, idle_power_column)