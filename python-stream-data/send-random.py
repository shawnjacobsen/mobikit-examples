#!/usr/bin/env python

import os
import json
import time
import argparse
from datetime import datetime

import geojson
import socketio

# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--feed-id", "-f", type=int, help="unique feed id", required=True)
parser.add_argument("--count", type=int, help="number of points to send", required=True)
parser.add_argument("--tags", "-d", type=str, default="{}", help="JSON object")
parser.add_argument("--debug", action="store_true", help="debug logging")

args = parser.parse_args()

# connect to the server
sio = socketio.Client(logger=args.debug)
sio.connect(
    os.getenv("MOBIKIT_STREAM_API_URL"),
    headers={"Authorization": "Token {}".format(os.getenv("MOBIKIT_API_TOKEN"))},
)

print("SID: {}".format(sio.sid))

# parse tags JSON object
tags = json.loads(args.tags)

# generate and send random points
for i in range(args.count):
    # assemble the GeoJSON feature
    feature = geojson.Feature(
        geometry=geojson.utils.generate_random("Point"), properties=tags
    )

    # assemble the SocketIO event
    event = {
        "headers": {"feed_id": args.feed_id, "timestamp": datetime.now().isoformat()},
        "feature": feature,
    }

    # emit the event on the "data" channel
    sio.emit("data", event, callback=print)

    # rate limit to one point per second
    time.sleep(1.0)

# disconnect from the server
sio.disconnect()

# XXX: SocketIO will eventually shut down background threads and quit but it
# takes a really long time. at this point we're fairly certain we don't need
# to wait for a response from the Stream API so just force quit the program
os._exit(0)
