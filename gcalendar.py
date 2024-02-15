from datetime import datetime, timedelta

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import utils


def get_calendar_events(credentials, calendars, days):
    try:
        service = build("calendar", "v3", credentials=credentials)

        # Call the Calendar API
        now = utils.round_to_nearest_five_minutes(datetime.utcnow())
        then = now + timedelta(days=days)

        items = [{"id": "primary"}]
        if calendars:
            for cal in calendars:
                items.append({"id": cal})

        body = {
            "timeMin": utils.convert_datetime_to_iso_string(now),
            "timeMax": utils.convert_datetime_to_iso_string(then),
            "items": items,
        }

        events_result = service.freebusy().query(body=body).execute()

        events = []
        for calendar in events_result["calendars"]:
            if "errors" in events_result["calendars"][calendar].keys():
                raise Exception(f"Calendar for {calendar} not found")
            events.extend(events_result["calendars"][calendar]["busy"])

        return events

    except HttpError as error:
        print(f"An error occurred: {error}")
