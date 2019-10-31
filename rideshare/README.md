# Mobikit Rideshare Demo

### Setup

This project depends on python3 with the `mobikit`, `flask`, and `flask_cors` packages.

In the Mobikit platform create a new workspace with `riders` and `drivers` as realtime feeds.

#### Environment Variables

Set the `MOBIKIT_API_TOKEN` variable with your API token.

#### Constants

`driver.html` and `rider.html` both have `<SETME_TOKEN>` and `<SETME_FEED_ID>`s which need to be replaced.

`rideshare.py` needs `<SETME_WORKSPACE_ID>` set to the project workspace ID.

#### Hosting

Clone this project and run with `./rideshare.py`.

The web security model requires a secure context to provide [Geolocation](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API), so any site must be hosted with https.
In general, if the device doesn't prompt you for location access the first time you open the site, it isn't working.

You can use [ngrok](https://ngrok.com/) with `ngrok http 8000` to foreword your local application to the web.

