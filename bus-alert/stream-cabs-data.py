#!/usr/bin/env python3

import os
import sys
import time
import json
import datetime
import argparse

import geojson
import requests
import socketio


# CABS bus routes
ROUTES = ["CLN", "CLS", "WC", "MC", "OW"]

# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--feed-id", "-f", type=int, help="unique feed id", required=True)
args = parser.parse_args()


def cabs_query(bus_route="MC"):
    """
    Make an HTTP request for cabs bus positions.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Referer": "https://www.osu.edu/map/",
            "DNT": "1",
        }
        params = (
            ("route", bus_route),
            ("getBus", "1"),
        )
        response = requests.get(
            "https://www.osu.edu/map/inc/google/v2/bus-data.php",
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        return response.json()
    except:
        return []


def next_route():
    """
    Generator to loop over the bus routes
    """
    nroutes = len(ROUTES)
    i = 0
    while True:
        yield ROUTES[i % nroutes]
        i = i + 1


# Main entry point
if __name__ == "__main__":

    # Make a connection to the Mobikit stream API
    sio = socketio.Client()
    sio.connect(
        os.getenv("MOBIKIT_STREAM_API_URL"),
        headers={"Authorization": "Token {}".format(os.getenv("MOBIKIT_API_TOKEN"))},
    )

    # loop over the routes indefinitely
    for route in next_route():
        timestamp = datetime.datetime.utcnow().isoformat()
        result = cabs_query(route)

        for bus in result:

            # Contruct a GeoJSON point
            point = geojson.Point((bus["lon"], bus["lat"]))
            tags = {
                "hdg": bus["hdg"],
                "vid": bus["vid"],
                "route": route,
                "timestamp": timestamp,
            }
            feature = geojson.Feature(geometry=point, properties=tags)

            # Emit the message with the points data to Mobikit
            message = {
                "headers": {"feed_id": args.feed_id, "timestamp": timestamp},
                "feature": feature,
            }
            print("EMIT: ", message)
            sio.emit("data", message)

        # Wait a bit for positions to change before requesting them again
        time.sleep(15 / len(ROUTES))
