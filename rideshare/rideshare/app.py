#!/usr/bin/env python3

import os
import json
import datetime
from pathlib import Path

from flask import Flask
from flask_cors import CORS
import mobikit

from rideshare import utils

print("PATH:", Path(__file__).parent.joinpath("templates"))

# Setup the Mobikit API client
MOBIKIT_API_TOKEN = os.getenv("MOBIKIT_API_TOKEN")
MOBIKIT_WORKSPACE_ID = int(os.getenv("MOBIKIT_WORKSPACE_ID"))
mobikit.set_api_key(MOBIKIT_API_TOKEN, environment="ohio")

# Setup the flask app
app = Flask(__name__, static_folder=Path(__file__).parent.joinpath("templates"))
CORS(app)

ride_requests = {}
active_rides = {}  # By ride_id
binding_driver = {}
binding_rider = {}

# Setup flask routes
@app.route("/")
def route_index():
    """
    Serve home page
    """
    return app.send_static_file("index.html")


@app.route("/driver")
def driver():
    """
    Serve driver app
    """
    return app.send_static_file("driver.html")


@app.route("/rider")
def rider():
    """
    Serve rider app
    """
    return app.send_static_file("rider.html")


@app.route("/rider/<int:rider_id>/request_ride")
def rider_request_ride(rider_id):
    """
    Route to request a ride
    """

    # Get the most recent rider position
    coords = None
    while coords is None:
        coords = utils.get_most_recent(
            mobikit,
            MOBIKIT_WORKSPACE_ID,
            "riders",
            lambda row: "rider_id" in row and row["rider_id"] == rider_id,
        )
    coords = json.loads(coords["point_geojson"])["coordinates"]

    obj = {
        "rider_id": rider_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "ride_id": utils.ride_id(),
        "rider_start_location": coords,
        "accepted": False,
    }
    ride_requests[rider_id] = obj
    return obj


@app.route("/rider/<int:rider_id>/status")
def rider_status(rider_id):
    """
    Get the status of a rider
    """
    ride = None
    if rider_id in ride_requests:
        ride = ride_requests[rider_id]
    elif rider_id in binding_rider:
        ride = active_rides[binding_rider[rider_id]]
    return {"ride": ride}


@app.route("/driver/<int:driver_id>/status")
def driver_status(driver_id):
    """
    Get the status of a driver
    """
    ride = None
    if driver_id in binding_driver:
        ride = active_rides[binding_driver[driver_id]]
    return {"ride": ride}


@app.route("/driver/<int:driver_id>/accept_ride")
def driver_get_request(driver_id):
    """
    Accept a ride request as a driver
    """

    # Get the driver positions
    coords = utils.get_most_recent(
        mobikit,
        MOBIKIT_WORKSPACE_ID,
        "drivers",
        lambda row: "driver_id" in row and row["driver_id"] == driver_id
    )
    if coords is None:
        return {"ride": None}
    coords = json.loads(coords["point_geojson"])["coordinates"]

    # Get the riders within range
    geo_circle_filter = {
        "type": "within",
        "field": "point",
        "meta": {"lng": coords[0], "lat": coords[1], "radius": 6400},  # meters
    }
    riders_in_range = None
    riders_in_range = utils.query_recent(
        mobikit, MOBIKIT_WORKSPACE_ID, "riders", query_filter=geo_circle_filter
    )
    chosen_rider = None
    for _, rider in riders_in_range.iterrows():
        if rider["tags"]["rider_id"] in ride_requests:
            chosen_rider = (rider, ride_requests[rider["tags"]["rider_id"]])
            break
        if chosen_rider is not None:
            break

    # Match ride requests to drivers
    ride = None
    if chosen_rider is not None:
        rider, request = chosen_rider
        request["accepted"] = True
        request["started"] = False
        request["driver_id"] = driver_id
        request["driver_start_location"] = coords

        # Create automation
        endpoint = "{}/webhook/ride_completed/{}/".format(os.getenv("PUBLIC_ADDRESS"), request["ride_id"])
        title = "auto-ride-{}".format(request["ride_id"])
        rider_start_location = request["rider_start_location"]
        feed = utils.get_feed_id(MOBIKIT_WORKSPACE_ID, 'drivers')
        triggers = [
            {
                "parent_template":6,
                "values": {
                    "side":"inside",
                    "center": {"type":"Point","coordinates":[rider_start_location[0], rider_start_location[1]]},"radius":1200
                    }
                }
            ]
        actions = [
                {"parent_template":4,
                "values":{"endpoint":endpoint}
                }
            ]
        request['automation_id'] = mobikit.automations.create(MOBIKIT_WORKSPACE_ID, title, feed, triggers, actions)

        # Update local references
        active_rides[request["ride_id"]] = request
        binding_driver[driver_id] = request["ride_id"]
        binding_rider[request["rider_id"]] = request["ride_id"]
        del ride_requests[request["rider_id"]]
        ride = request

    return {"ride": ride}

@app.route("/webhook/ride_completed/<string:ride_id>/", methods = ['GET', 'POST'])
def ride_completed(ride_id):
    if ride_id not in active_rides:
        return {}
    active_rides[ride_id]["started"] = True
    mobikit.automations.delete(MOBIKIT_WORKSPACE_ID, active_rides[ride_id]["automation_id"])
    return {}

# Run the flask app
def main():
    """
    Run the flask server.
    """
    app.run(port=8000)
