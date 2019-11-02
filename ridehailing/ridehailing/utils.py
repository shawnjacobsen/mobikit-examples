import datetime
import secrets
import mobikit


def window_start_timestamp():
    """
    Get the start time in isoformat
    """
    return (
        datetime.datetime.utcnow() - datetime.timedelta(seconds=15)
    ).isoformat() + "Z"


def query_recent(mobikit, workspace_id, feed_name, query_filter=None):
    """
    Query for recent driver positions
    """

    # Build the query
    query = {
        "select": [
            {"field": "id"},
            {"field": "tm"},
            {"field": "tags"},
            {"field": "point", "format": "geojson"},
        ],
        "sort": [
            {"field": "tm", "dir": "descending"},
            {"field": "id", "dir": "ascending"},
        ],
        "filter": {
            "conjunction": "and",
            "predicates": [
                {
                    "type": "gt",
                    "field": "tm",
                    "meta": {"comparand": window_start_timestamp()},
                }
            ],
        },
    }
    if query_filter is not None:
        query["filter"]["predicates"].append(query_filter)

    # Request the data from Mobikit
    print("Recent positions query:", query)
    df = mobikit.workspaces.load(workspace_id, feed_name, query=query)

    return df


def get_most_recent(mobikit, workspace_id, feed_name, tag_filter, query_filter=None):
    """
    Retrieve the most recent position
    """

    # Get the most recent
    df = query_recent(mobikit, workspace_id, feed_name, query_filter)
    points = df[df["tags"].apply(tag_filter)]
    if points.shape[0] == 0:
        return None

    return points.loc[0]


def ride_id():
    """
    Generate a ride id
    """
    return secrets.token_hex(15)

def get_feed_id(workspace_id, feed_name):
    workspaces = mobikit.workspaces.search('')
    workspaces = list(filter(lambda w: w["workspace_id"] == workspace_id, workspaces))
    if len(workspaces) < 1:
        return None
    feeds = workspaces[0]['feeds']
    for feed_id, name in feeds.items():
        if name == feed_name:
            return feed_id
    return None
