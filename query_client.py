from flask import Flask, jsonify, request
import requests
import yaml

with open("config/config.yml", "r") as f:
        config = yaml.safe_load(f)
HOST = config["SERVER"]["HOST"]
PORT = config["SERVER"]["PORT"]
server_url = "http://" + HOST + ":" + PORT

_start_time = "2022-12-12T07:39:00.000Z"
_end_time = "2022-12-12T07:40:00.000Z"
_target_container = "rapl"
_metric = "power"
_sensor = "obelix94"

request_json = {'start_time': _start_time , 'end_time': _end_time, 'entity': "container", 'metric': _metric, 'sensor': _sensor, 'target': _target_container}
server_response = requests.post(f'{server_url}/power_consumption', json= request_json)
server_json = server_response.json()
print(server_json)
print()

_start_time = "2022-12-12T07:39:00.000Z"
_end_time = "2022-12-12T07:40:00.000Z"
_target_container = "hwpc-sensor"
_metric = "energy"
_sensor = "obelix94"

energy_request_json = {'start_time': _start_time , 'end_time': _end_time, 'entity': "container", 'metric': _metric, 'sensor': _sensor, 'target': _target_container}
energy_server_response = requests.post(f'{server_url}/power_consumption', json= energy_request_json)
energy_server_json = energy_server_response.json()
print(energy_server_json)
print()

_start_time = "2022-12-11T18:32:00.000Z"
_end_time = "2022-12-11T20:32:00.000Z"
_metric = "carbon_intensity"
_zone = "US-NY-NYIS"

carbon_request_json = {'start_time': _start_time , 'end_time': _end_time, 'zone': _zone, 'metric': _metric}
carbon_server_response = requests.post(f'{server_url}/carbon_intensity', json= carbon_request_json)
carbon_server_json = carbon_server_response.json()
print(carbon_server_json)
print()

_start_time = "2022-12-14T22:19:41.000Z"
_end_time = "2022-12-14T22:29:11.000Z"
_metric = "carbon_emission"
_target_container = "hwpc-sensor"
_sensor = "obelix94"
_zone = "US-NY-NYIS"

carbon_emission_request_json = {'start_time': _start_time , 'end_time': _end_time, 'entity': "container", 'metric': _metric, 'sensor': _sensor, 'target': _target_container, "zone": _zone}
carbon_emission_server_response = requests.post(f'{server_url}/carbon_emission', json= carbon_emission_request_json)
carbon_emission_server_json = carbon_emission_server_response.json()
print(carbon_emission_server_json)
print()

_start_time = "2022-12-14T22:19:41.000Z"
_end_time = "2022-12-14T22:29:11.000Z"
_metric = "carbon_emission"
_target_app = "hwpc-sensor"
_zone = "US-NY-NYIS"

carbon_emission_request_json_app = {'start_time': _start_time , 'end_time': _end_time, 'entity': "application", 'metric': _metric, 'sensor': _sensor, 'target': _target_app, "zone": _zone}
carbon_emission_server_response_app = requests.post(f'{server_url}/carbon_emission', json= carbon_emission_request_json_app)
carbon_emission_server_json_app = carbon_emission_server_response_app.json()
print(carbon_emission_server_json_app)
print()

_start_time = "2022-12-12T07:39:00.000Z"
_end_time = "2022-12-12T07:40:00.000Z"
_target_container = "global"
_metric = "power"

request_json = {'start_time': _start_time , 'end_time': _end_time, 'metric': _metric, 'entity': "application", 'target':_target_container}
server_response = requests.post(f'{server_url}/power_consumption', json= request_json)
server_json = server_response.json()
print(server_json)
print()

_start_time = "2022-12-12T07:39:00.000Z"
_end_time = "2022-12-12T07:40:00.000Z"
_target_container = "global"
_metric = "energy"

request_json = {'start_time': _start_time , 'end_time': _end_time, 'metric': _metric, 'entity': "application", 'target':_target_container}
server_response = requests.post(f'{server_url}/power_consumption', json= request_json)
server_json = server_response.json()
print(server_json)
print()

if __name__ == "__main__":
    pass
    