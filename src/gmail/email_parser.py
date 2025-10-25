import re
import logging
from datetime import datetime
from typing import Dict, List, Optional
from email.utils import parsedate_to_datetime

logger = logging.getLogger(__name__)

class EmailParser:
    """Parse and extract structured information from emails"""
    
    def __init__(self):
        # Common patterns for extracting dates and deadlines
        self.date_patterns = [
            r'deadline[:\s]+([^,\n]+)',
            r'due[:\s]+([^,\n]+)',
            r'by[:\s]+([^,\n]+)',
            r'until[:\s]+([^,\n]+)',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}',
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{4}'
        ]
        
        # Common patterns for extracting times
        self.time_patterns = [
            r'(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM))',
            r'(\d{1,2}\s*(?:am|pm|AM|PM))',
            r'at\s+(\d{1,2}:\d{2})',
            r'(\d{1,2}:\d{2})'
        ]
        
        # Keywords that indicate quest-worthy content
        self.quest_keywords = [
            'assignment', 'homework', 'project', 'exam', 'test', 'quiz',
            'deadline', 'due', 'submit', 'complete', 'finish',
            'meeting', 'appointment', 'event', 'conference', 'workshop',
            'interview', 'presentation', 'review', 'assessment',
            'application', 'registration', 'enrollment', 'signup'
        ]
    
    def extract_deadline(self, text: str) -> Optional[datetime]:
        """Extract deadline from email text"""
        try:
            text_lower = text.lower()
            
            for pattern in self.date_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    try:
                        # Try to parse the date
                        if isinstance(match, tuple):
                            match = match[0]
                        
                        # Clean up the match
                        match = match.strip()
                        
                        # Try different date formats
                        date_formats = [
                            '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d',
                            '%B %d, %Y', '%b %d, %Y',
                            '%d/%m/%Y', '%d-%m-%Y'
                        ]
                        
                        for fmt in date_formats:
                            try:
                                return datetime.strptime(match, fmt)
                            except ValueError:
                                continue
                        
                        # Try email.utils parser
                        try:
                            return parsedate_to_datetime(match)
                        except:
                            continue
                            
                    except Exception:
                        continue
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract deadline: {e}")
            return None
    
    def extract_duration(self, text: str) -> Optional[int]:
        """Extract event duration in minutes from email text"""
        try:
            text_lower = text.lower()
            
            # Look for duration patterns
            duration_patterns = [
                r'(\d+)\s*(?:minutes?|mins?)',
                r'(\d+)\s*(?:hours?|hrs?)',
                r'(\d+)\s*(?:days?)',
                r'duration[:\s]+(\d+)',
                r'length[:\s]+(\d+)'
            ]
            
            for pattern in duration_patterns:
                matches = re.findall(pattern, text_lower)
                for match in matches:
                    try:
                        duration = int(match)
                        
                        # Convert to minutes based on context
                        if 'hour' in pattern or 'hr' in pattern:
                            return duration * 60
                        elif 'day' in pattern:
                            return duration * 24 * 60
                        else:
                            return duration
                            
                    except ValueError:
                        continue
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract duration: {e}")
            return None
    
    def is_quest_worthy(self, subject: str, body: str) -> bool:
        """Determine if email should become a quest"""
        try:
            text = f"{subject} {body}".lower()
            
            # Check for quest keywords
            keyword_count = sum(1 for keyword in self.quest_keywords if keyword in text)
            
            # Check for action words
            action_words = ['complete', 'submit', 'attend', 'participate', 'register', 'apply']
            action_count = sum(1 for word in action_words if word in text)
            
            # Check for deadline indicators
            deadline_indicators = ['deadline', 'due', 'by', 'until', 'before']
            deadline_count = sum(1 for word in deadline_indicators if word in text)
            
            # Scoring system
            score = keyword_count + action_count + deadline_count
            
            # Must have at least 2 indicators to be quest-worthy
            return score >= 2
            
        except Exception as e:
            logger.warning(f"Failed to determine if quest-worthy: {e}")
            return False
    
    def extract_quest_type(self, subject: str, body: str) -> str:
        """Extract quest type from email content"""
        try:
            text = f"{subject} {body}".lower()
            
            # Assignment/Homework
            if any(word in text for word in ['assignment', 'homework', 'project']):
                return 'assignment'
            
            # Assessment
            elif any(word in text for word in ['exam', 'test', 'quiz', 'assessment']):
                return 'assessment'
            
            # Event
            elif any(word in text for word in ['meeting', 'event', 'conference', 'workshop', 'seminar']):
                return 'event'
            
            # Application
            elif any(word in text for word in ['application', 'apply', 'registration', 'enroll']):
                return 'application'
            
            # Interview
            elif any(word in text for word in ['interview', 'interviewing']):
                return 'interview'
            
            # Presentation
            elif any(word in text for word in ['presentation', 'presenting', 'present']):
                return 'presentation'
            
            # Default
            else:
                return 'task'
                
        except Exception as e:
            logger.warning(f"Failed to extract quest type: {e}")
            return 'task'
    
    def parse_email(self, email_data: Dict) -> Dict:
        """Parse email and extract structured information"""
        try:
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            
            parsed = {
                'is_quest_worthy': self.is_quest_worthy(subject, body),
                'quest_type': self.extract_quest_type(subject, body),
                'deadline': self.extract_deadline(f"{subject} {body}"),
                'duration_minutes': self.extract_duration(f"{subject} {body}"),
                'original_subject': subject,
                'original_body': body
            }
            
            return parsed
            
        except Exception as e:
            logger.error(f"Failed to parse email: {e}")
            return {
                'is_quest_worthy': False,
                'quest_type': 'task',
                'deadline': None,
                'duration_minutes': None,
                'original_subject': email_data.get('subject', ''),
                'original_body': email_data.get('body', '')
            }

