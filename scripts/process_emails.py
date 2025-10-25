#!/usr/bin/env python3
"""
Main email processing script for the Solo Leveling System.
This script orchestrates the entire email processing pipeline.
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.database.db_manager import DatabaseManager
from src.gmail.gmail_client import GmailClient
from src.gmail.email_parser import EmailParser
from src.llm.quest_analyzer import QuestAnalyzer
from src.gcalendar.calendar_client import CalendarClient
from src.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailProcessor:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.gmail_client = GmailClient()
        self.email_parser = EmailParser()
        self.quest_analyzer = QuestAnalyzer()
        self.calendar_client = CalendarClient()
    
    def process_emails(self, days: int = None) -> Dict[str, int]:
        """Process emails from the last N days"""
        try:
            days = days or settings.DEFAULT_DAYS_TO_PROCESS
            logger.info(f"Starting email processing for last {days} days")
            
            # Get last processing datetime
            last_processed = self.db_manager.get_last_processing_datetime()
            start_date = last_processed if last_processed else None
            
            # Fetch emails from Gmail
            logger.info("Fetching emails from Gmail...")
            emails = self.gmail_client.get_emails(days=days, start_date=start_date)
            logger.info(f"Fetched {len(emails)} emails")
            
            # Store emails in database
            logger.info("Storing emails in database...")
            stored_emails = 0
            for i, email in enumerate(emails):
                try:
                    # Debug logging for first few emails
                    if i < 3:
                        logger.info(f"Email {i}: sender='{email.get('sender', 'MISSING')}', subject='{email.get('subject', 'MISSING')}', body_length={len(email.get('body', ''))}, received_date={email.get('received_date', 'MISSING')}")
                    
                    email_id = self.db_manager.add_email(
                        email_id=email['email_id'],
                        sender=email['sender'],
                        subject=email['subject'],
                        body=email['body'],
                        received_date=email['received_date']
                    )
                    if email_id:
                        stored_emails += 1
                except Exception as e:
                    logger.warning(f"Failed to store email {email.get('email_id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Stored {stored_emails} emails")
            
            # Process unprocessed emails
            logger.info("Processing unprocessed emails...")
            unprocessed_emails = self.db_manager.get_unprocessed_emails()
            logger.info(f"Found {len(unprocessed_emails)} unprocessed emails")
            
            quests_created = 0
            calendar_events_created = 0
            
            for email in unprocessed_emails:
                try:
                    # Analyze email for quest creation
                    analysis = self.quest_analyzer.analyze_email_for_quest(email)
                    
                    if analysis.get('should_create_quest', False):
                        # Create quest in database
                        quest_id = self.db_manager.add_quest(
                            email_id=email['id'],
                            title=analysis['title'],
                            description=analysis['description'],
                            quest_type=analysis['quest_type'],
                            importance=analysis['importance'],
                            urgency=analysis['urgency'],
                            deadline=analysis.get('deadline'),
                            event_duration_minutes=analysis.get('event_duration_minutes', 60)
                        )
                        
                        if quest_id:
                            quests_created += 1
                            logger.info(f"Created quest: {analysis['title']}")
                            
                            # Create calendar event if quest has deadline
                            if analysis.get('deadline'):
                                try:
                                    quest_data = {
                                        'title': analysis['title'],
                                        'description': analysis['description'],
                                        'quest_type': analysis['quest_type'],
                                        'importance': analysis['importance'],
                                        'urgency': analysis['urgency'],
                                        'deadline': analysis['deadline'],
                                        'event_duration_minutes': analysis.get('event_duration_minutes', 60)
                                    }
                                    
                                    calendar_event_id = self.calendar_client.create_quest_event(quest_data)
                                    if calendar_event_id:
                                        self.db_manager.update_quest_calendar_event_id(quest_id, calendar_event_id)
                                        calendar_events_created += 1
                                        logger.info(f"Created calendar event: {calendar_event_id}")
                                        
                                except Exception as e:
                                    logger.warning(f"Failed to create calendar event for quest {quest_id}: {e}")
                    
                    # Mark email as processed
                    self.db_manager.mark_email_processed(email['id'])
                    
                except Exception as e:
                    logger.error(f"Failed to process email {email['id']}: {e}")
                    continue
            
            # Log processing statistics
            processing_datetime = datetime.now()
            self.db_manager.log_processing(
                last_processed_datetime=processing_datetime,
                emails_processed=len(unprocessed_emails),
                quests_created=quests_created
            )
            
            logger.info(f"Email processing completed:")
            logger.info(f"  - Emails processed: {len(unprocessed_emails)}")
            logger.info(f"  - Quests created: {quests_created}")
            logger.info(f"  - Calendar events created: {calendar_events_created}")
            
            return {
                'emails_processed': len(unprocessed_emails),
                'quests_created': quests_created,
                'calendar_events_created': calendar_events_created
            }
            
        except Exception as e:
            logger.error(f"Email processing failed: {e}")
            raise
    
    def process_emails_for_user(self, user_id: str, user_preferences: Dict, days: int = 7) -> Dict[str, int]:
        """Process emails for a specific user with their preferences"""
        try:
            logger.info(f"Processing emails for user {user_id} with preferences")
            
            # Fetch emails from Gmail
            emails = self.gmail_client.get_emails(days=days)
            logger.info(f"Fetched {len(emails)} emails from last {days} days")
            
            # Store emails in database
            stored_emails = 0
            for email in emails:
                try:
                    email_id = self.db_manager.add_email(
                        email_id=email['email_id'],
                        sender=email['sender'],
                        subject=email['subject'],
                        body=email['body'],
                        received_date=email['received_date']
                    )
                    if email_id:
                        stored_emails += 1
                except Exception as e:
                    logger.warning(f"Failed to store email {email.get('email_id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Stored {stored_emails} emails")
            
            # Get unprocessed emails for this user
            unprocessed_emails = self.db_manager.get_unprocessed_emails()
            logger.info(f"Found {len(unprocessed_emails)} unprocessed emails")
            
            quests_created = 0
            
            for email in unprocessed_emails:
                try:
                    # Analyze email for quest creation with user preferences
                    analysis = self.quest_analyzer.analyze_email_for_quest(email, user_preferences)
                    
                    if analysis.get('should_create_quest', False):
                        # Create quest in database with user_id
                        quest_id = self.db_manager.add_quest(
                            user_id=user_id,
                            email_id=email['id'],
                            title=analysis['title'],
                            description=analysis['description'],
                            quest_type=analysis['quest_type'],
                            quest_category=analysis.get('quest_category', 'general'),
                            importance=analysis['importance'],
                            urgency=analysis['urgency'],
                            deadline=analysis.get('deadline'),
                            event_duration_minutes=analysis.get('event_duration_minutes', 60)
                        )
                        
                        if quest_id:
                            quests_created += 1
                            logger.info(f"Created quest for user {user_id}: {analysis['title']}")
                    
                    # Mark email as processed
                    self.db_manager.mark_email_processed(email['id'])
                    
                except Exception as e:
                    logger.error(f"Failed to process email {email.get('id', 'unknown')}: {e}")
                    continue
            
            # Log processing session
            processing_datetime = datetime.now()
            self.db_manager.log_processing(
                last_processed_datetime=processing_datetime,
                emails_processed=len(unprocessed_emails),
                quests_created=quests_created
            )
            
            logger.info(f"Email processing completed for user {user_id}")
            logger.info(f"Emails processed: {len(unprocessed_emails)}")
            logger.info(f"Quests created: {quests_created}")
            
            return {
                'emails_processed': len(unprocessed_emails),
                'quests_created': quests_created,
                'daily_quests_created': 0  # Daily tasks are created during onboarding
            }
            
        except Exception as e:
            logger.error(f"Failed to process emails for user {user_id}: {e}")
            raise

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process emails for Solo Leveling System')
    parser.add_argument('--days', type=int, default=settings.DEFAULT_DAYS_TO_PROCESS,
                       help=f'Number of days to process (default: {settings.DEFAULT_DAYS_TO_PROCESS})')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        processor = EmailProcessor()
        results = processor.process_emails(days=args.days)
        
        print(f"\n✅ Email processing completed successfully!")
        print(f"📧 Emails processed: {results['emails_processed']}")
        print(f"🎯 Quests created: {results['quests_created']}")
        print(f"📅 Calendar events created: {results['calendar_events_created']}")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

