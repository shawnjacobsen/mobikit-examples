# Python Stream Data

This folder contains example Python scripts for sending data to the Stream API. The following scripts are included:

- `send-one.py`: script to send one data point
- `send-random.py`: script to send random data points

## Requirements

- Python 3.6+

## Quick Start

Start by cloning this repo and navigating into this example's directory:

```bash
git clone https://github.com/mobikitinc/mobikit-examples.git
cd mobikit-examples/python-stream-data
```

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

Set environment variables for the Mobikit Stream API URL and your Mobikit API token. You can get your Mobikit API token by navigating to Mobikit and copying it from your user settings page. Here is an example of how to set environment variables in `bash`:

```bash
export MOBIKIT_STREAM_API_URL='https://stream.ohio.mobikit.io/'
export MOBIKIT_API_TOKEN='FILL_ME_IN'
```

Now you can run the scripts:

```bash
# Note that `feed-id` should be a Mobikit Realtime Feed ID
./send-one.py --feed-id 86 -x '-83.039358' -y '39.998030' --tags '{"vehicle_id": 10}'
```

The scripts have a `--help` flag that will print out some usage information and describe the flags used above.
