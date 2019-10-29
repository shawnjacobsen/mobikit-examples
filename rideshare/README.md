# Mobikit Rideshare Demo

### Setup

This project depends on python3 with the `flask` and `flask_cors` packages.


Set the `MOBIKIT_API_TOKEN` variable with your API token.

Clone this project and run with `./rideshare.py`.

The web security model requires a secure context to provide [Geolocation](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API), so any site must be hosted with https.
In general, if the device doesn't prompt you for location access the first time you open the site, it isn't working.

You can use [ngrok](https://ngrok.com/): `ngrok http 8000` to foreword your local application to the web.

