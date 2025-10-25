#!/usr/bin/env python3
"""
Script to create calendar events for existing quests that don't have calendar events yet.
This mimics the same process as the email processing script.
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
from src.gcalendar.calendar_client import CalendarClient
from src.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CalendarEventCreator:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.calendar_client = CalendarClient()
    
    def create_calendar_events_for_quests(self, user_id: str = None) -> Dict[str, int]:
        """Create calendar events for quests that don't have them yet"""
        try:
            # Get quests without calendar events
            if user_id:
                quests = self.db_manager.get_user_quests_without_calendar_events(user_id)
            else:
                quests = self.db_manager.get_quests_without_calendar_events()
            
            if not quests:
                logger.info("No quests found without calendar events")
                return {
                    'quests_processed': 0,
                    'calendar_events_created': 0,
                    'errors': 0
                }
            
            logger.info(f"Found {len(quests)} quests without calendar events")
            
            calendar_events_created = 0
            errors = 0
            
            for quest in quests:
                try:
                    quest_id = quest['id']
                    quest_title = quest['title']
                    
                    # Skip if quest doesn't have a deadline
                    if not quest.get('deadline'):
                        logger.info(f"Skipping quest {quest_id} '{quest_title}' - no deadline")
                        continue
                    
                    # Prepare quest data for calendar event
                    quest_data = {
                        'title': quest_title,
                        'description': quest['description'],
                        'quest_type': quest['quest_type'],
                        'importance': quest['importance'],
                        'urgency': quest['urgency'],
                        'deadline': quest['deadline'],
                        'event_duration_minutes': quest.get('event_duration_minutes', 60)
                    }
                    
                    # Create calendar event
                    calendar_event_id = self.calendar_client.create_quest_event(quest_data)
                    
                    if calendar_event_id:
                        # Update quest with calendar event ID
                        self.db_manager.update_quest_calendar_event_id(quest_id, calendar_event_id)
                        calendar_events_created += 1
                        logger.info(f"Created calendar event for quest {quest_id} '{quest_title}': {calendar_event_id}")
                    else:
                        logger.warning(f"Failed to create calendar event for quest {quest_id} '{quest_title}'")
                        errors += 1
                        
                except Exception as e:
                    logger.error(f"Failed to create calendar event for quest {quest.get('id', 'unknown')}: {e}")
                    errors += 1
                    continue
            
            logger.info(f"Calendar event creation completed:")
            logger.info(f"  - Quests processed: {len(quests)}")
            logger.info(f"  - Calendar events created: {calendar_events_created}")
            logger.info(f"  - Errors: {errors}")
            
            return {
                'quests_processed': len(quests),
                'calendar_events_created': calendar_events_created,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Failed to create calendar events: {e}")
            raise

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create calendar events for existing quests')
    parser.add_argument('--user-id', type=str, help='Specific user ID to process (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        creator = CalendarEventCreator()
        results = creator.create_calendar_events_for_quests(user_id=args.user_id)
        
        print(f"\n✅ Calendar event creation completed successfully!")
        print(f"📋 Quests processed: {results['quests_processed']}")
        print(f"📅 Calendar events created: {results['calendar_events_created']}")
        print(f"❌ Errors: {results['errors']}")
        
    except Exception as e:
        logger.error(f"Calendar event creation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
