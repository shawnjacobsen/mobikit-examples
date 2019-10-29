#!/usr/bin/env python3

from flask import Flask
from flask_cors import CORS
import os
import datetime
import json

import mobikit

MOBIKIT_API_TOKEN = os.getenv('MOBIKIT_API_TOKEN')
mobikit.set_api_key(MOBIKIT_API_TOKEN)

app = Flask(__name__, static_folder=os.path.abspath(os.getcwd()))
CORS(app)

WORKSPACE_ID = 185

ride_requests = {}

active_rides = {} # By ride_id
binding_driver = {}
binding_rider = {}

@app.route("/")
def route_index():
    return app.send_static_file('index.html')

@app.route("/driver")
def driver():
    return app.send_static_file('driver2.html')

@app.route("/rider")
def rider():
    return app.send_static_file('rider2.html')

def window_start_timestamp():
    ts = (datetime.datetime.utcnow() - datetime.timedelta(seconds=15)).isoformat() + 'Z'
    return ts

def query_recent(feed_name, query_filter=None):
    query = {
        "select":[{"field":"id"},{"field":"tm"},{"field":"tags"},{"field":"point","format":"geojson"}],
        "sort":[{"field":"tm","dir":"descending"},{"field":"id","dir":"ascending"}],
        "filter":{"conjunction":"and","predicates":[{"type":"gt","field":"tm","meta":{"comparand":window_start_timestamp()}}]}
    }
    if query_filter is not None:
        query['filter']['predicates'].append(query_filter)
    print(query)
    df = mobikit.workspaces.load(WORKSPACE_ID, feed_name, query=query)
    return df

def get_most_recent(feed_name, tag_filter, query_filter=None):
    df = query_recent(feed_name, query_filter)
    points = df[df['tags'].apply(tag_filter)]
    if points.shape[0] == 0:
        return None
    return points.loc[0]

def ride_id():
    import secrets
    return secrets.token_hex(15)

@app.route("/rider/<int:rider_id>/request_ride")
def rider_request_ride(rider_id):
    coords = None
    while coords is None:
        coords = get_most_recent('riders', lambda row: 'rider_id' in row and row['rider_id'] == rider_id)
    coords = json.loads(coords['point_geojson'])['coordinates']

    obj = {'rider_id': rider_id, 'timestamp': datetime.datetime.now().isoformat(),'ride_id': ride_id(), 'rider_start_location': coords, 'accepted': False}
    ride_requests[rider_id] = obj
    return obj

@app.route("/rider/<int:rider_id>/status")
def rider_status(rider_id):
    ride = None
    if rider_id in ride_requests:
        ride = ride_requests[rider_id]
    elif rider_id in binding_rider:
        ride = active_rides[binding_rider[rider_id]]
    return {'ride': ride}

@app.route("/driver/<int:driver_id>/status")
def driver_status(driver_id):
    ride = None
    if driver_id in binding_driver:
        ride = active_rides[binding_driver[driver_id]]
    return {'ride': ride}

@app.route("/driver/<int:driver_id>/accept_ride")
def driver_get_request(driver_id):
    coords = get_most_recent('drivers', lambda row: 'driver_id' in row and row['driver_id'] == driver_id)
    if coords is None:
        return {'ride': None}
    coords = json.loads(coords['point_geojson'])['coordinates']

    geo_circle_filter = {
        'type': 'within',
        'field': 'point',
        'meta': {
            'lng': coords[0],
            'lat': coords[1],
            'radius': 6400 # meters
        }
    }
    riders_in_range = None
    riders_in_range = query_recent('riders', query_filter=geo_circle_filter)

    chosen_rider = None
    for _, rider in riders_in_range.iterrows():
        if rider['tags']['rider_id'] in ride_requests:
            chosen_rider = (rider, ride_requests[rider['tags']['rider_id']])
            break
        if chosen_rider is not None:
            break
    
    ride = None
    if chosen_rider is not None:
        rider, request = chosen_rider
        request['accepted'] = True
        request['driver_id'] = driver_id
        request['driver_start_location'] = coords
        active_rides[request['ride_id']] = request
        binding_driver[driver_id] = request['ride_id']
        binding_rider[request['rider_id']] = request['ride_id']
        del ride_requests[request['rider_id']]
        ride = request

    return {'ride': ride}

app.run(port=8000)
