import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_credentials():
    """Handles Google API credentials."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def list_upcoming_events(service):
    """Lists the next 10 upcoming events."""
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    try:
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        if not events:
            print("No upcoming events found.")
        else:
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                print(start, event["summary"])
    except HttpError as error:
        print(f"An error occurred: {error}")

def create_event(service):
    """Creates a new event."""
    event = {
        "summary": "My Python Event",
        "location": "Somewhere Online",
        "description": "Some more details on this awesome event",
        "colorId": 3,
        "start": {
            "dateTime": "2024-09-10T09:00:00+02:00",
            "timeZone": "Europe/Berlin"  # Adjust this as needed
        },
        "end": {
            "dateTime": "2024-09-10T19:00:00+02:00",
            "timeZone": "Europe/Berlin"  # Adjust this as needed
        },
        "recurrence": [
            "RRULE:FREQ=DAILY;COUNT=3"
        ],
        "attendees": [
            {"email": "social@neuralnine.com"},
            {"email": "somemailthathopefullydoesnotexist@mail.com"}
        ]
    }
    try:
        event = service.events().insert(calendarId="primary", body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")
    except HttpError as error:
        print(f"An error occurred: {error}")

def main():
    """Main function to handle both reading and writing events."""
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    # Example of listing upcoming events
    list_upcoming_events(service)

    # Example of creating a new event
    create_event(service)

if __name__ == "__main__":
    main()
