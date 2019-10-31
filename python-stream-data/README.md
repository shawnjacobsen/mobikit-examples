# Python Stream Data

This folder contains example Python scripts for sending data to the Stream API.

* `send-one.py`: script to send one data point
* `send-random.py`: script to send random data points

## Requirements

* Python 3.6+

## Quick Start

Create a Python virtual environment using the Python interpreter you want to
use (i.e. `python3` is Python 3.6 on my machine):

```bash
python3 -m venv my_venv
```

Activate the virtual environment and install required packages:

```bash
source my_venv/bin/activate
pip install -r requirements.txt
```

Set environment variables for the Stream API URL and your API token:

```bash
export MOBIKIT_STREAM_API_URL='https://stream.ohio.mobikit.io/'
export MOBIKIT_API_TOKEN='FILL_ME_IN'
```

Now you can run the scripts:

```bash
./send-one.py -f 86 -x '-83.039358' -y '39.998030' --tags '{"vehicle_id": 10}'
```

The scripts have a `--help` flag that will print out some usage information.
