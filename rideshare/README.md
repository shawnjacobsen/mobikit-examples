# Ridesharing Example

This folder contains an end-to-end example ridesharing application built using Mobikit. Note that this example uses some Javascript uses some features that are only available in modern browsers (Chrome, Firefox, Edge, etc.)

## Requirements

- Python 3.6+

## Quick Start

Start by cloning this repo and navigating into this example's directory:

```bash
git clone https://github.com/mobikitinc/mobikit-examples.git
cd mobikit-examples/rideshare
```

To setup the application, you'll need to create 2 realtime feeds within Mobikit, one for drivers and one for riders. Then, fill in the variables in the following files:

- **templates/driver.html**

  - set `DRIVER_FEED_ID` to the Mobikit realtime driver feed

  - set `MOBIKIT_API_TOKEN` to a Mobikit API token

- **templates/rider.html**

  - set `RIDER_FEED_ID` to the Mobikit realtime rider feed

  - set `MOBIKIT_API_TOKEN` to a Mobikit API token

Next, create a Python virtual environment using the Python interpreter you want to use (i.e. `python3` is Python 3.6 on my machine):

```bash
python3 -m venv my_venv
```

Activate the virtual environment and install required packages:

```bash
source my_venv/bin/activate
python3 setup.py install
```

Set environment variables for the Mobikit Stream API URL and your Mobikit API token. You can get your Mobikit API token by navigating to Mobikit and copying it from your user settings page. Here is an example of how to set environment variables in `bash`:

```bash
export MOBIKIT_API_TOKEN='<my_api_token>'
export MOBIKIT_WORKSPACE_ID='<my_workspace_id>'
export PUBLIC_ADDRESS=`<public_endpoint>` # eg https://example.com

```

Now you can run the application:

```bash
start-rideshare
```

The web security model requires a secure context to provide [Geolocation](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API), so any site must be hosted with https. In general, if the device doesn't prompt you for location access the first time you open the site, it isn't working.

You can use [ngrok](https://ngrok.com/) to forward your local application to the web:

```bash
ngrok http 8000
```
