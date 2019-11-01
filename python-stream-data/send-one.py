#!/usr/bin/env python

import os
import json
import sys
import argparse
from datetime import datetime

import geojson
import socketio

# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--feed-id", "-f", type=int, help="unique feed id", required=True)

parser.add_argument("--latitude", "-y", type=float, help="latitude", required=True)

parser.add_argument("--longitude", "-x", type=float, help="longitude", required=True)

parser.add_argument(
    "--timestamp",
    "-t",
    type=str,
    default=datetime.now().isoformat(),
    help="timestamp in ISO8601 format",
)

parser.add_argument("--tags", "-d", type=str, default="{}", help="JSON object")

args = parser.parse_args()
sio = socketio.Client()

# parse the timestamp as ISO8601 (Python compatible)
try:
    timestamp = datetime.strptime(args.timestamp, "%Y-%m-%dT%H:%M:%S.%f")

except ValueError as e:
    print("Failed to parse timestamp: {}".format(e))
    sys.exit(1)

# connect to the server
sio.connect(
    os.getenv("MOBIKIT_STREAM_API_URL"),
    headers={"Authorization": "Token {}".format(os.getenv("MOBIKIT_API_TOKEN"))},
)

# assemble the GeoJSON feature
feature = geojson.Feature(
    geometry=geojson.Point((args.longitude, args.latitude)),
    properties=json.loads(args.tags),
)

# assemble the SocketIO event
event = {
    "headers": {"feed_id": args.feed_id, "timestamp": timestamp.isoformat()},
    "feature": feature,
}

# emit the event on the "data" channel and call print() with the response
sio.emit("data", event, callback=print)

# wait for SocketIO to finish processing messages and callbacks
sio.sleep(1.0)

# disconnect from the server
sio.disconnect()
