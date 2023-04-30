from influxdb_client import InfluxDBClient
import pandas as pd
from flask import Flask, jsonify, request
import requests
import datetime
import warnings
import yaml
import json
from influxdb_client.client.warnings import MissingPivotFunction
import flux_templates
warnings.simplefilter("ignore", MissingPivotFunction)

app = Flask(__name__)

with open("config/config.yml", "r") as f:
    config = yaml.safe_load(f)
HOST = config["SERVER"]["HOST"]
PORT = config["SERVER"]["PORT"]
INFLUX_HOST = config["INFLUX"]["HOST"]
INFLUX_PORT = config["INFLUX"]["PORT"]
influx_url = "http://" + INFLUX_HOST + ":" + INFLUX_PORT
influx_token = config["INFLUX"]["TOKEN"]
influx_org = config["INFLUX"]["ORG"]
DATETIME_STRING_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

client = InfluxDBClient(url=influx_url, 
                token=influx_token, 
                org=influx_org)

def get_power(start_time_str, stop_time_str, container_name, sensor):
    try:
        start_time = datetime.datetime.strptime(start_time_str, DATETIME_STRING_FORMAT)
        stop_time = datetime.datetime.strptime(stop_time_str, DATETIME_STRING_FORMAT)
        with open('flux_templates/power_consumption_query.flux', 'r') as f:
            power_consumption_flux_template = f.read()
        result = {}
        result["metric"] = "power"
        result["entity"] = "container"
        result["start time"] = start_time_str
        result["end time"] = stop_time_str
        result["sensor"] = sensor
        result["target"] = container_name
        result["unit"] = "W"
        if( start_time == stop_time ):
            stop_time = start_time + datetime.timedelta(seconds = 1)
            stop_time_str = stop_time.strftime(DATETIME_STRING_FORMAT)
            flux_query = power_consumption_flux_template.format(start_time = start_time_str, stop_time = stop_time_str, sensor = sensor, container_name = container_name)
            output_tables = client.query_api().query(flux_query)
            for table in output_tables:
                result["data"] = [r["power"] for r in table.records][0]
        else:
            flux_query = power_consumption_flux_template.format(start_time = start_time_str, stop_time = stop_time_str, sensor = sensor, container_name = container_name)
            output_tables = client.query_api().query(flux_query)
            for table in output_tables:
                result["data"] = [r["power"] for r in table.records]
        if result.get("data") == None:
            return json.dumps({"error" : "power data unavailable for the given input parameters"})
        return json.dumps(result)
    except Exception as e: 
        print(e)
        return json.dumps({"error" : "an error occurred while processing the request for power"})

def get_energy(start_time_str, stop_time_str, container_name, sensor):
    try:
        if(start_time_str == stop_time_str):
            return json.dumps({"error" : "start time and stop time need to be different to get the energy"})
        with open('flux_templates/energy_consumption_query.flux', 'r') as f:
            energy_consumption_flux_template = f.read()
        flux_query = energy_consumption_flux_template.format(start_time = start_time_str, stop_time = stop_time_str, sensor = sensor, container_name = container_name)
        output_tables = client.query_api().query(flux_query)
        result = {}
        result["metric"] = "energy"
        result["entity"] = "container"
        result["start time"] = start_time_str
        result["end time"] = stop_time_str
        result["sensor"] = sensor
        result["target"] = container_name
        result["unit"] = "J"
        for table in output_tables:
            for record in table.records:
                result["value"] = record["_value"]
        if result.get("value") == None:
            return json.dumps({"error" : "energy data unavailable for the given input parameters"})
        return json.dumps(result)
    except Exception as e: 
        print(e)
        return json.dumps({"error" : "an error occurred while processing the request for energy"})

def get_carbon_intensity(start_time_str, stop_time_str, zone):
    try:
        start_time = datetime.datetime.strptime(start_time_str, DATETIME_STRING_FORMAT)
        stop_time = datetime.datetime.strptime(stop_time_str, DATETIME_STRING_FORMAT)
        with open('flux_templates/carbon_intensity_query.flux', 'r') as f:
            carbon_intensity_flux_template = f.read()
        result = {}
        result["metric"] = "carbon intensity"
        result["start time"] = start_time_str
        result["end time"] = stop_time_str
        result["zone"] = zone
        result["unit"] = "gCO2eq/kWh"
        if( start_time == stop_time ): 
            stop_time = start_time + datetime.timedelta(seconds = 1)
            stop_time_str = stop_time.strftime(DATETIME_STRING_FORMAT)
            flux_query = carbon_intensity_flux_template.format(start_time = start_time_str, stop_time = stop_time_str, zone = zone)
            tables = client.query_api().query(flux_query)
            for table in tables:
                result["data"] = [r["carbonIntensityAvg"] for r in table.records][0]
        else:
            flux_query = carbon_intensity_flux_template.format(start_time = start_time_str, stop_time = stop_time_str, zone = zone)
            tables = client.query_api().query(flux_query)
            for table in tables:
                result["data"] = [r["carbonIntensityAvg"] for r in table.records]
        if result.get("data") == None:
            return json.dumps({"error" : "carbon intensity data unavailable for the given input parameters"})
        return json.dumps(result)
    except Exception as e: 
        print(e)
        return json.dumps({"error" : "an error occurred while processing the request for carbon intensity"})

def get_carbon_emission(start_time_str, stop_time_str, target, sensor, zone):
    try:
        if(start_time_str == stop_time_str):
            return json.dumps({"error" : "start time and stop time need to be different to get carbon emission"})
        with open('flux_templates/carbon_emission_query.flux', 'r') as f:
            carbon_emission_flux_template = f.read()
        result = {}

        start_time = datetime.datetime.strptime(start_time_str, DATETIME_STRING_FORMAT)
        start_time_carbon_intensity = start_time - datetime.timedelta(hours = 1)
        start_time_carbon_intensity_str = start_time_carbon_intensity.strftime(DATETIME_STRING_FORMAT)

        flux_query = carbon_emission_flux_template.format(start_time = start_time_str, stop_time = stop_time_str, target = target, sensor = sensor, start_time_carbon_intensity = start_time_carbon_intensity_str, zone = zone)    
        output_tables = client.query_api().query(flux_query)
        result["metric"] = "carbon emission"
        result["entity"] = "container"
        result["start time"] = start_time_str
        result["end time"] = stop_time_str
        result["sensor"] = sensor
        result["target"] = target
        result["unit"] = "gCO2"
        for table in output_tables:
            result["value"] = [r["carbon_emission"] for r in table.records][0]
        if result.get("value") == None:
            return json.dumps({"error" : "carbon emission data unavailable for the given input parameters"})
        return json.dumps(result)
    except Exception as e: 
        print(e)
        return json.dumps({"error" : "an error occurred while processing the request for carbon emission"})

def get_carbon_emission_per_application(start_time_str, stop_time_str, target, zone):
    try:
        if(start_time_str == stop_time_str):
            return json.dumps({"error" : "start time and stop time need to be different to get carbon emission"})  
        with open('flux_templates/carbon_emission_per_application_query.flux', 'r') as f:
            carbon_emission_per_application_flux_template = f.read()
        result = {}

        start_time = datetime.datetime.strptime(start_time_str, DATETIME_STRING_FORMAT)
        start_time_carbon_intensity = start_time - datetime.timedelta(hours = 1)
        start_time_carbon_intensity_str = start_time_carbon_intensity.strftime(DATETIME_STRING_FORMAT)

        flux_query = carbon_emission_per_application_flux_template.format(start_time = start_time_str, stop_time = stop_time_str, target = target, start_time_carbon_intensity = start_time_carbon_intensity_str, zone = zone)
        output_tables = client.query_api().query(flux_query)
        result["metric"] = "carbon emission"
        result["entity"] = "application"
        result["start time"] = start_time_str
        result["end time"] = stop_time_str
        result["target"] = target
        result["unit"] = "gCO2"
        for table in output_tables:
            result["value"] = [r["carbon_emission"] for r in table.records][0]
        if result.get("value") == None:
            return json.dumps({"error" : "carbon emission data unavailable for the given input parameters"})
        return json.dumps(result)
    except Exception as e: 
        print(e)
        return json.dumps({"error" : "an error occurred while processing the request for application carbon emission"})

def get_application_power(start_time_str, stop_time_str, application_name):
    try:
        start_time = datetime.datetime.strptime(start_time_str, DATETIME_STRING_FORMAT)
        stop_time = datetime.datetime.strptime(stop_time_str, DATETIME_STRING_FORMAT)
        if( start_time == stop_time ): 
            stop_time = start_time + datetime.timedelta(seconds = 1)
            stop_time_str = stop_time.strftime(DATETIME_STRING_FORMAT)
        with open('flux_templates/power_consumption_per_application_query.flux', 'r') as f:
            power_consumption_per_application_flux_template = f.read()
        flux_query = power_consumption_per_application_flux_template.format(start_time = start_time_str, stop_time = stop_time_str, application_name = application_name)
        output_tables = client.query_api().query(flux_query)
        result = {}
        result["metric"] = "power"
        result["entity"] = "application"
        result["start time"] = start_time_str
        result["end time"] = stop_time_str
        result["unit"] = "W"
        result["value"] = []
        for table in output_tables:
            for record in table.records:
                result["value"] += [r["_value"] for r in table.records]
        if result.get("value") == None:
            return json.dumps({"error" : f"application({application_name}) power data unavailable for the given input parameters"})
        return json.dumps(result)
    except Exception as e:
        print(e)
        return json.dumps({"error" : "an error occurred while processing the request for application power"}) 

def get_application_energy(start_time_str, stop_time_str, application_name):
    try:
        if(start_time_str == stop_time_str):
            return json.dumps({"error" : f"start time and stop time need to be different to get the energy of application ({application_name})"})
        with open('flux_templates/energy_consumption_per_application_query.flux', 'r') as f:
            energy_consumption_per_application_flux_template = f.read()
        flux_query = energy_consumption_per_application_flux_template.format(start_time = start_time_str, stop_time = stop_time_str, application_name = application_name)
        output_tables = client.query_api().query(flux_query)
        result = {}
        result["metric"] = "energy"
        result["entity"] = "application"
        result["start time"] = start_time_str
        result["end time"] = stop_time_str
        result["target"] = application_name
        result["unit"] = "J"
        for table in output_tables:
            for record in table.records:
                result["value"] = record["_value"]
        if result.get("value") == None:
            return json.dumps({"error" : f"application({application_name}) energy data unavailable for the given input parameters"})
        return json.dumps(result)
    except Exception as e:
        print(e)
        return json.dumps({"error" : "an error occurred while processing the request for application energy"}) 

@app.route('/power_consumption', methods=['POST'])
def serve_request ():
    json_body = request.get_json()
    start_time_str = json_body['start_time']
    stop_time_str = json_body['end_time']
    entity = json_body['entity']
    metric = json_body['metric']
    container_name = json_body['target']
    response_json = []
    if metric.strip().lower() == "power" and entity.strip().lower() == "container":
        sensor = json_body['sensor']
        response_json = get_power(start_time_str, stop_time_str, container_name, sensor)
    elif metric.strip().lower() == "energy" and entity.strip().lower() == "container":
        sensor = json_body['sensor']
        response_json = get_energy(start_time_str, stop_time_str, container_name, sensor)
    elif metric.strip().lower() == "power" and entity.strip().lower() == "application": 
        response_json = get_application_power(start_time_str, stop_time_str, container_name)
    elif metric.strip().lower() == "energy" and entity.strip().lower() == "application":
        response_json = get_application_energy(start_time_str, stop_time_str, container_name)
    else:
        return json.dumps({"error" : "please input valid metric and/or entity"}) 
    return response_json

@app.route('/carbon_intensity', methods=['POST'])
def serve_carbon_request ():
    json_body = request.get_json()
    start_time_str = json_body['start_time']
    stop_time_str = json_body['end_time']
    zone = json_body['zone']
    metric = json_body['metric']
    response_json = []
    if metric.strip().lower() == "carbon_intensity" :
        response_json = get_carbon_intensity(start_time_str, stop_time_str, zone)
    else:
        return json.dumps({"error" : "please input valid metric and/or entity"}) 
    return response_json

@app.route('/carbon_emission', methods=['POST'])
def serve_carbon_emission_request ():
    json_body = request.get_json()
    start_time_str = json_body['start_time']
    stop_time_str = json_body['end_time']
    metric = json_body['metric']
    target = json_body['target']
    entity = json_body['entity']
    zone = json_body['zone']
    response_json = []
    if metric.strip().lower() == "carbon_emission" and entity == "container":
        sensor = json_body['sensor']
        response_json = get_carbon_emission(start_time_str, stop_time_str, target, sensor, zone)
    elif metric.strip().lower() == "carbon_emission" and entity == "application":
        response_json = get_carbon_emission_per_application(start_time_str, stop_time_str, target, zone)
    else:
        return json.dumps({"error" : "please input valid metric and/or entity"}) 
    return response_json

app.run(host = HOST ,port = PORT, threaded=True)