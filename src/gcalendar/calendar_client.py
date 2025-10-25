import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.config.settings import settings

logger = logging.getLogger(__name__)

class CalendarClient:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.service = None
        self.credentials = None
    
    def authenticate(self):
        """Authenticate with Google Calendar API using OAuth2"""
        try:
            creds = None
            token_path = 'credentials/calendar_token.json'
            
            # Load existing credentials
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # Check if client_secret.json exists
                    client_secret_path = 'credentials/client_secret.json'
                    if not os.path.exists(client_secret_path):
                        raise FileNotFoundError(
                            f"OAuth credentials not found at {client_secret_path}. "
                            "Please run 'python scripts/setup_oauth.py' to set up credentials."
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        client_secret_path, self.SCOPES)
                    
                    # Use a fixed port
                    creds = flow.run_local_server(
                        port=3000, 
                        open_browser=True
                    )
                
                # Save credentials for next run
                os.makedirs('credentials', exist_ok=True)
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.credentials = creds
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Calendar authentication successful")
            
        except Exception as e:
            logger.error(f"Calendar authentication failed: {e}")
            raise
    
    def create_quest_event(self, quest_data: Dict) -> Optional[str]:
        """Create calendar event for quest"""
        try:
            if not self.service:
                self.authenticate()
            
            # Prepare event data
            event = self._prepare_event_data(quest_data)
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            event_id = created_event.get('id')
            logger.info(f"Calendar event created: {event_id}")
            
            return event_id
            
        except HttpError as e:
            logger.error(f"Calendar API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create calendar event: {e}")
            raise
    
    def _prepare_event_data(self, quest_data: Dict) -> Dict:
        """Prepare event data for calendar creation"""
        try:
            title = quest_data.get('title', 'Untitled Quest')
            description = quest_data.get('description', '')
            quest_type = quest_data.get('quest_type', 'task')
            importance = quest_data.get('importance', 'side_quest')
            urgency = quest_data.get('urgency', 'low')
            deadline = quest_data.get('deadline')
            duration_minutes = quest_data.get('event_duration_minutes', 60)
            
            # Set start time
            if deadline:
                # Handle both datetime objects and string dates
                if isinstance(deadline, str):
                    # Parse string date (assuming ISO format)
                    start_time = datetime.fromisoformat(deadline.replace('Z', ''))
                else:
                    start_time = deadline
            else:
                # Default to tomorrow at 9 AM if no deadline
                start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
            
            # Set end time
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Format times for Google Calendar
            start_time_str = start_time.isoformat() + 'Z'
            end_time_str = end_time.isoformat() + 'Z'
            
            # Create event description with quest details
            event_description = f"""
Quest Type: {quest_type.title()}
Importance: {importance.replace('_', ' ').title()}
Urgency: {urgency.title()}

{description}

---
Generated by Solo Leveling System
"""
            
            # Set event color based on urgency
            color_id = self._get_color_id_for_urgency(urgency)
            
            # Create event
            event = {
                'summary': f"🎯 {title}",
                'description': event_description.strip(),
                'start': {
                    'dateTime': start_time_str,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time_str,
                    'timeZone': 'UTC',
                },
                'colorId': color_id,
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 60},       # 1 hour before
                    ],
                },
            }
            
            return event
            
        except Exception as e:
            logger.error(f"Failed to prepare event data: {e}")
            raise
    
    def _get_color_id_for_urgency(self, urgency: str) -> str:
        """Get color ID based on urgency level"""
        color_mapping = {
            'critical': '11',  # Red
            'high': '6',       # Orange
            'medium': '5',      # Yellow
            'low': '10'        # Green
        }
        return color_mapping.get(urgency, '1')  # Default to blue
    
    def update_quest_event(self, event_id: str, quest_data: Dict) -> bool:
        """Update existing calendar event"""
        try:
            if not self.service:
                self.authenticate()
            
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update event data
            updated_event = self._prepare_event_data(quest_data)
            updated_event['id'] = event_id
            
            # Update the event
            self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=updated_event
            ).execute()
            
            logger.info(f"Calendar event updated: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Failed to update calendar event: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to update calendar event: {e}")
            return False
    
    def delete_quest_event(self, event_id: str) -> bool:
        """Delete calendar event"""
        try:
            if not self.service:
                self.authenticate()
            
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            logger.info(f"Calendar event deleted: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Failed to delete calendar event: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete calendar event: {e}")
            return False
    
    def get_quest_events(self, max_results: int = 100) -> list:
        """Get all quest events from calendar"""
        try:
            if not self.service:
                self.authenticate()
            
            # Search for events with quest emoji
            events_result = self.service.events().list(
                calendarId='primary',
                q='🎯',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"Found {len(events)} quest events")
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get quest events: {e}")
            return []

