"""get_google_calendar.py

get Google Calendar events via your Google Calendar API.
"""

import datetime
import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DATETIME_FMT = "%Y-%m-%dT%H:%M:%SZ"

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

CREDENTIALS_PATH = os.environ["GOOGLE_OAUTH2_CREDENTIALS"]

TOKEN_PATH = os.environ["GOOGLE_CALENDAR_TOKEN"]

CALENDAR_IDS = None
with open(os.environ["GOOGLE_CALENDAR_ID"], "r") as ff:
    CALENDAR_IDS = json.loads(ff.read())


def get_events(calendar_id: str = "primary", start_time: str = None, end_time: str = None, max_results: int = 10):
    """retrieve the event list registered in your Google Calendar via the Google Calendar API.

    Parameters
    ----------
    calendar_id : str
        Calendar ID.
    start_time : str
        datetime to retrieve events from.
    end_time : str
        datetime to retrieve events until.
    max_results : int
        max number of events to retrieve.

    Returns
    -------
    events : List[Dict]
        list of events.
        Check the following URL or more detail of each event:
        https://developers.google.com/calendar/api/v3/reference/events?hl=ja#resource
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    if not start_time:
        start_time = datetime.datetime.now().strftime(DATETIME_FMT)
    if not end_time:
        end_time = "2038-12-31T23:59:59Z"
    
    events = []
    try:
        service = build("calendar", "v3", credentials=creds)
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime"
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")

        return events

    except HttpError as error:
        print(f"An error occurred: {error}")


def get_todays_events(calendar_id: str = "primary", max_results: int = 10):
    """retrieve today's event list registered in your Google Calendar via the Google Calendar API.

    Parameters
    ----------
    calendar_id : str
        Calendar ID.
    max_results : int
        max number of events to retrieve.

    Returns
    -------
    events : List[Dict]
        list of events.
        Check the following URL or more detail of each event:
        https://developers.google.com/calendar/api/v3/reference/events?hl=ja#resource
    """
    today = datetime.datetime.today()
    start_time = today.date().strftime(DATETIME_FMT)
    end_time = datetime.datetime(today.year, today.month, today.day, 23, 59, 59).strftime(DATETIME_FMT)
    print(end_time)
    return get_events(calendar_id, start_time, end_time, max_results)


if __name__ == "__main__":
    events = get_events()
    # Prints the start and name of the next 10 events
    print("upcoming primary events:")
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])

    events = get_todays_events()
    # Prints the start and name of the next 10 events
    print("upcoming today's primary events:")
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])
    