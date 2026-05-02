
import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Authenticate and return Google Calendar service"""
    creds = None

    # Token file stores user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def create_calendar_event(
    doctor_name: str,
    patient_name: str,
    date: str,
    start_time: str,
    end_time: str,
    reason: str = "General checkup"
):
    """Create a Google Calendar event for the appointment"""
    try:
        service = get_calendar_service()

        # Build datetime strings
        start_datetime = f"{date}T{start_time}:00"
        end_datetime = f"{date}T{end_time}:00"

        event = {
            'summary': f"Appointment: {patient_name} with {doctor_name}",
            'description': f"Patient: {patient_name}\nDoctor: {doctor_name}\nReason: {reason}",
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'Asia/Kolkata',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }

        event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()

        print(f"[Calendar] Event created: {event.get('htmlLink')}")
        return {
            "success": True,
            "event_id": event['id'],
            "event_link": event.get('htmlLink')
        }

    except Exception as e:
        print(f"[Calendar] Error creating event: {e}")
        return {"success": False, "error": str(e)}
    
if __name__ == "__main__":
    service = get_calendar_service()
    print("Google Calendar authenticated successfully!")