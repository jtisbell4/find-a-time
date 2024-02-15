import warnings

warnings.simplefilter(action="ignore", category=DeprecationWarning)

from datetime import datetime, timedelta

import pandas as pd
import pytz

import utils
from auth import get_credentials
from gcalendar import get_calendar_events

creds = get_credentials()


def main(calendars, days=5, timezone="US/Eastern"):
    now = utils.round_to_nearest_five_minutes(datetime.utcnow())
    then = now + timedelta(days=days)

    events = get_calendar_events(credentials=creds, calendars=calendars, days=days)

    busy_times = utils.discretize_busy_events(events)
    all_times = utils.create_time_grid(start=now, end=then)

    # Get items from all_times that are not in busy_times
    free_times = utils.get_free_times(all_times, busy_times)

    series = pd.Series(free_times).diff()
    gaps = series[series > timedelta(seconds=600)]

    free_blocks = utils.split_list_by_indices(free_times, gaps.index)

    eastern = pytz.timezone(timezone)

    for block in free_blocks:
        start_of_free_block = min(block).astimezone(eastern)
        end_of_free_block = max(block).astimezone(eastern) + timedelta(minutes=5)
        print(
            start_of_free_block.strftime("%m/%d %I:%M %p")
            + "-"
            + end_of_free_block.strftime("%I:%M %p")
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--timezone",
        default="US/Eastern",
        type=str,
        help="timezone to report timeslots in",
    )
    parser.add_argument(
        "attendees",
        type=str,
        nargs="*",
        help="email addresses of attendees",
    )
    args = parser.parse_args()

    main(calendars=args.attendees, timezone=args.timezone)
