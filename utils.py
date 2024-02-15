from datetime import datetime, timedelta

import pytz

GRID = timedelta(minutes=5)


def round_to_nearest_five_minutes(dt, type="floor"):
    # Zero out seconds and microseconds
    dt = dt.replace(second=0, microsecond=0)
    minutes = dt.minute

    if type == "ceiling":
        minutes_to_add = (5 - dt.minute % 5) % 5
        # Add the necessary minutes
        dt += timedelta(minutes=minutes_to_add)
    else:
        # Calculate how many minutes to subtract to round down to the nearest 5
        excess_minutes = minutes % 5
        dt -= timedelta(minutes=excess_minutes)
    return dt


def split_list_by_indices(lst, indices):
    # Initialize the starting index and the result list
    start = 0
    result = []

    # Iterate over the indices
    for index in indices:
        # Slice the list from the starting index to the current index
        result.append(lst[start:index])
        # Update the starting index to be the current index
        start = index

    # Append the remaining elements after the last index
    result.append(lst[start:])

    return result


def convert_datetime_to_iso_string(dt):
    return dt.isoformat() + "Z"


def discretize_busy_events(events):
    busy_times = []
    for event in events:
        start = round_to_nearest_five_minutes(datetime.fromisoformat(event["start"]))
        end = round_to_nearest_five_minutes(
            datetime.fromisoformat(event["end"]), type="ceiling"
        )

        while start < end:
            busy_times.append(start)
            start += GRID

    busy_times.sort()
    return busy_times


def create_time_grid(start, end):
    utc = pytz.timezone("UTC")
    start, end = utc.localize(start), utc.localize(end)

    all_times = []
    while start <= end:
        if (start.hour >= 13) and (start.hour <= 23) and (start.weekday() < 5):
            all_times.append(start)
        start += GRID
    return all_times


def get_free_times(all_times, busy_times):
    free_times = set(all_times).difference(set(busy_times))

    free_times = list(free_times)
    free_times.sort()
    return free_times
