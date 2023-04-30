import yaml
import csv
import argparse
import datetime
import os
from pytz import timezone

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
    
def writeCarbonData(timestamp_column, carbon_intensity_column, zone_name_column):
    input_files_path = config["CARBON_DATA"]["FILES_PATH"]
    print(input_files_path)
    for file in os.listdir(input_files_path):
        if file.endswith(".csv"):
            inputfile = open(input_files_path + "/" + file, 'r')
            print("input file " + file + " read at location " + input_files_path)

            batchsize = 5000
            datapoints = []
            with inputfile as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',')
                count = 0
                for row in reader:
                    count += 1
                    print(row[timestamp_column] + " "+row[zone_name_column])

                    unix_s = row[timestamp_column]

                    timeDate = datetime.datetime.fromtimestamp(int(unix_s))
                    print(timeDate)

                    point = Point("carbon_intensity").field("carbonIntensityAvg", int(row[carbon_intensity_column])).tag("zoneName", row[zone_name_column]).time(timeDate)

                    print(point)
                    datapoints.append(point)
                    if len(datapoints) % batchsize == 0:
                        print('Read %d lines'%count)
                        print('Inserting %d datapoints...'%(len(datapoints)))
                        
                        write_api.write(bucket = carbon_bucket, org = influx_org, record = datapoints)

                        datapoints = []

                    print(count)

            if len(datapoints) > 0:
                print('Read %d lines'%count)
                print('Inserting %d datapoints...'%(len(datapoints)))

                write_api.write(bucket = carbon_bucket, org = influx_org, record = datapoints)

    print('Done')


def writeRealTimeCarbonData(timestamp_column, carbon_intensity_column, zone_name_column):
    input_files_path = config["CARBON_DATA"]["FILES_PATH"]
    print(input_files_path)
    for file in os.listdir(input_files_path):
        if file.endswith(".csv"):
            inputfile = open(input_files_path + "/" + file, 'r')
            print("input file " + file + " read at location " + input_files_path)

            datapoints = []
            lastKLines = 3
            with inputfile as csvfile:
                lines = csvfile.readlines()
                columns = lines[0].rstrip().split(',')

                timestampIndex = getColumnIndexInFile(columns, timestamp_column)
                if timestampIndex == -1:
                    continue

                carbonIntensityIndex = getColumnIndexInFile(columns, carbon_intensity_column)
                if carbonIntensityIndex == -1:
                    continue

                zoneNameIndex = getColumnIndexInFile(columns, zone_name_column)
                if zoneNameIndex == -1:
                    continue

                for line in lines[-lastKLines:]:
                    data = line.rstrip().split(',')

                    unix_s = data[timestampIndex]

                    timeDate = datetime.datetime.fromtimestamp(int(unix_s))

                    point = Point("carbon_intensity").field("carbonIntensityAvg", int(data[carbonIntensityIndex])).tag("zoneName", data[zoneNameIndex]).time(timeDate)

                    print(point)
                    datapoints.append(point)

                write_api.write(bucket = carbon_bucket, org = influx_org, record = datapoints)

            print('Done')

def getColumnIndexInFile(columns, column_name):
    for index, column in enumerate(columns):
        if column == column_name:
            return index
    return -1

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Get the mode for writing carbon intensity data to influx bucket')        # Parse the arguments from command prompt

    parser.add_argument("--write_mode", "-write_mode", required=True, type=str, choices=['realtime', 'simulation'], help='Write Mode')
    parser.add_argument("--timestamp_column", "-timestamp", required=False, type=str, default = "timestamp")
    parser.add_argument("--carbon_intensity_column", "-carbon_intensity", required=False, type=str, default = "carbon_intensity_avg")
    parser.add_argument("--zone_name_column", "-zone_name", required=False, type=str, default = "zone_name")
    parser.add_argument("--config_file_path", "-config_path", required=False, type=str, default = "../config/config.yml")
    args = parser.parse_args()


    write_mode = args.write_mode
    print("Writing data in "+ write_mode+ " mode")

    timestamp_column = args.timestamp_column
    carbon_intensity_column = args.carbon_intensity_column
    zone_name_column = args.zone_name_column
    config_file_path = args.config_file_path
    print(config_file_path)
    with open(config_file_path, "r") as f:
        config = yaml.safe_load(f)

    HOST = config["INFLUX"]["HOST"]
    PORT = config["INFLUX"]["PORT"]
    influx_url = "http://" + HOST + ":" + PORT
    influx_token = config["INFLUX"]["TOKEN"]
    influx_org = config["INFLUX"]["ORG"]

    influx_client = InfluxDBClient(url = influx_url, token = influx_token, org = influx_org)
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    carbon_bucket = config["INFLUX"]["CARBON_INTENSITY_BUCKET"]
    # Checking if bucket already exists
    bucket_api = influx_client.buckets_api()
    # If we can't find the bucket, we create it
    if bucket_api.find_bucket_by_name(carbon_bucket) is None:
        bucket_api.create_bucket(bucket_name = carbon_bucket, org_id = influx_org)


    if write_mode == "realtime":
        writeRealTimeCarbonData(timestamp_column, carbon_intensity_column, zone_name_column)
    elif write_mode == "simulation":
        writeCarbonData(timestamp_column, carbon_intensity_column, zone_name_column)