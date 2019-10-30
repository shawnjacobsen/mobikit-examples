#!/usr/bin/env python3

import requests
import time
import json
import geojson
import datetime
import sys
import os

import socketio


ROUTES = ['CLN', 'CLS', 'WC', 'MC', 'OW']


if len(sys.argv) < 2:
    print('Usage: {} <FEED ID>'.format(sys.argv[0]))
    sys.exit(-1)

def cabs_query(bus_route='MC'):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': 'https://www.osu.edu/map/',
            'DNT': '1',
        }
        params = (
            ('route', bus_route),
            ('getBus', '1'),
        )
        response = requests.get('https://www.osu.edu/map/inc/google/v2/bus-data.php', headers=headers, params=params)
        assert response.status_code == 200
        return json.loads(response.text)
    except:
        return []

def next_route():
    nroutes = len(ROUTES)
    i = 0
    while True:
        yield ROUTES[i % nroutes]
        i = i + 1

sio = socketio.Client()
sio.connect(
    os.getenv("MOBIKIT_STREAM_API_URL"),
    headers={
        "Authorization": "Token {}".format(os.getenv("MOBIKIT_API_TOKEN"))
    }
)

for route in next_route():
    timestamp = datetime.datetime.utcnow().isoformat()
    result = cabs_query(route)
    for bus in result:
        point = geojson.Point((bus['lon'],bus['lat']))
        tags = {'hdg': bus['hdg'], 'vid': bus['vid'], 'route': route, 'timestamp': timestamp}
        feature = geojson.Feature(geometry=point, properties=tags)
        # print(feature)

        message = {
            "headers": {
                "feed_id": int(sys.argv[1]),
                "timestamp": datetime.datetime.now().isoformat()
            },
            "feature": feature
        }
        print('EMIT: ', message)
        sio.emit('data', message)

    time.sleep(15/len(ROUTES))
