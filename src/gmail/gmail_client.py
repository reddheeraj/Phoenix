import os
import base64
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.config.settings import settings

logger = logging.getLogger(__name__)

class GmailClient:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self):
        self.service = None
        self.credentials = None
    
    def authenticate(self):
        """Authenticate with Gmail API using OAuth2"""
        try:
            creds = None
            token_path = 'credentials/gmail_token.json'
            
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
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail authentication successful")
            
        except Exception as e:
            logger.error(f"Gmail authentication failed: {e}")
            raise
    
    def get_emails(self, days: int = 7, start_date: datetime = None) -> List[Dict]:
        """Fetch emails from the last N days"""
        try:
            if not self.service:
                self.authenticate()
            
            # Calculate date range
            if start_date:
                after_date = start_date
            else:
                after_date = datetime.now() - timedelta(days=days)
            
            # Format date for Gmail API
            after_date_str = after_date.strftime('%Y/%m/%d')
            
            # Query for emails
            query = f'after:{after_date_str}'
            
            # Get message IDs
            results = self.service.users().messages().list(
                userId='me', 
                q=query,
                maxResults=1000
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            # Fetch full email details
            for message in messages:
                try:
                    msg = self.service.users().messages().get(
                        userId='me', 
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    email_data = self._parse_email(msg)
                    if email_data:
                        emails.append(email_data)
                        
                except Exception as e:
                    logger.warning(f"Failed to fetch email {message['id']}: {e}")
                    continue
            
            logger.info(f"Fetched {len(emails)} emails from last {days} days")
            return emails
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get emails: {e}")
            raise
    
    def _parse_email(self, msg: Dict) -> Optional[Dict]:
        """Parse email message into structured data"""
        try:
            headers = msg['payload'].get('headers', [])
            
            # Extract headers
            email_data = {
                'email_id': msg['id'],
                'sender': '',
                'subject': '',
                'body': '',
                'received_date': None
            }
            
            # Parse headers
            for header in headers:
                name = header['name'].lower()
                value = header['value']
                
                if name == 'from':
                    email_data['sender'] = value
                elif name == 'subject':
                    email_data['subject'] = value
                elif name == 'date':
                    try:
                        # Parse RFC 2822 date format
                        from email.utils import parsedate_to_datetime
                        email_data['received_date'] = parsedate_to_datetime(value)
                    except:
                        email_data['received_date'] = datetime.now()
            
            # Extract body
            email_data['body'] = self._extract_body(msg['payload'])
            
            # Only return if we have essential data
            if email_data['sender'] and email_data['subject']:
                return email_data
            else:
                return None
                
        except Exception as e:
            logger.warning(f"Failed to parse email: {e}")
            return None
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        try:
            body = ""
            
            if 'parts' in payload:
                # Multipart message
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    elif part['mimeType'] == 'text/html' and not body:
                        if 'data' in part['body']:
                            body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            else:
                # Single part message
                if payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
                elif payload['mimeType'] == 'text/html' and 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
            
            # Clean up body text
            if body:
                # Remove HTML tags if present
                import re
                body = re.sub(r'<[^>]+>', '', body)
                # Clean up whitespace
                body = ' '.join(body.split())
            
            return body[:5000]  # Limit body length
            
        except Exception as e:
            logger.warning(f"Failed to extract email body: {e}")
            return ""

