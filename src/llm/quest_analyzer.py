import logging
from datetime import datetime
from typing import Dict, Any, Optional
from src.llm.bedrock_client import BedrockClient
from src.gmail.email_parser import EmailParser

logger = logging.getLogger(__name__)

class QuestAnalyzer:
    def __init__(self):
        self.bedrock_client = BedrockClient()
        self.email_parser = EmailParser()
    
    def analyze_email_for_quest(self, email_data: Dict, user_preferences: Dict = None) -> Dict[str, Any]:
        """Analyze email and determine if it should become a quest, aligned with user's long-term goals"""
        try:
            # First, use email parser for basic analysis
            parsed_email = self.email_parser.parse_email(email_data)
            
            # If not quest-worthy based on basic parsing, return early
            if not parsed_email['is_quest_worthy']:
                return {
                    'should_create_quest': False,
                    'reasoning': 'Email does not contain quest-worthy content based on basic analysis'
                }
            
            # Use LLM for detailed analysis with user preferences
            llm_analysis = self.bedrock_client.generate_quest_analysis_with_goals(email_data, user_preferences)
            
            # Validate and clean the LLM response
            validated_analysis = self._validate_llm_response(llm_analysis, parsed_email)
            
            logger.info(f"Quest analysis completed for email: {email_data.get('subject', 'No subject')}")
            return validated_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze email for quest: {e}")
            return {
                'should_create_quest': False,
                'reasoning': f'Analysis failed: {str(e)}'
            }
    
    def _validate_llm_response(self, llm_analysis: Dict, parsed_email: Dict) -> Dict[str, Any]:
        """Validate and clean LLM response"""
        try:
            # Ensure required fields exist
            validated = {
                'should_create_quest': llm_analysis.get('should_create_quest', False),
                'title': llm_analysis.get('title', ''),
                'description': llm_analysis.get('description', ''),
                'quest_type': llm_analysis.get('quest_type', 'task'),
                'importance': llm_analysis.get('importance', 'side_quest'),
                'urgency': llm_analysis.get('urgency', 'low'),
                'deadline': llm_analysis.get('deadline'),
                'event_duration_minutes': llm_analysis.get('event_duration_minutes', 60),
                'reasoning': llm_analysis.get('reasoning', '')
            }
            
            # Validate quest type
            valid_quest_types = ['assignment', 'assessment', 'event', 'application', 'interview', 'presentation', 'task']
            if validated['quest_type'] not in valid_quest_types:
                validated['quest_type'] = 'task'
            
            # Validate importance
            valid_importance = ['daily', 'weekly', 'main_quest', 'side_quest']
            if validated['importance'] not in valid_importance:
                validated['importance'] = 'side_quest'
            
            # Validate urgency
            valid_urgency = ['low', 'medium', 'high', 'critical']
            if validated['urgency'] not in valid_urgency:
                validated['urgency'] = 'low'
            
            # Parse deadline if provided
            if validated['deadline']:
                try:
                    if isinstance(validated['deadline'], str):
                        validated['deadline'] = datetime.fromisoformat(validated['deadline'].replace('Z', '+00:00'))
                except:
                    validated['deadline'] = None
            
            # Use parsed email deadline if LLM didn't provide one
            if not validated['deadline'] and parsed_email.get('deadline'):
                validated['deadline'] = parsed_email['deadline']
            
            # Use parsed email duration if LLM didn't provide one
            if validated['event_duration_minutes'] == 60 and parsed_email.get('duration_minutes'):
                validated['event_duration_minutes'] = parsed_email['duration_minutes']
            
            # Ensure title and description are not empty if creating quest
            if validated['should_create_quest']:
                if not validated['title']:
                    validated['title'] = email_data.get('subject', 'Untitled Quest')
                if not validated['description']:
                    validated['description'] = f"Quest based on email: {email_data.get('subject', 'No subject')}"
            
            return validated
            
        except Exception as e:
            logger.error(f"Failed to validate LLM response: {e}")
            return {
                'should_create_quest': False,
                'reasoning': f'Validation failed: {str(e)}'
            }
    
    def create_quest_from_analysis(self, analysis: Dict, email_id: int) -> Optional[Dict[str, Any]]:
        """Create quest data from analysis results"""
        try:
            if not analysis.get('should_create_quest', False):
                return None
            
            quest_data = {
                'email_id': email_id,
                'title': analysis['title'],
                'description': analysis['description'],
                'quest_type': analysis['quest_type'],
                'importance': analysis['importance'],
                'urgency': analysis['urgency'],
                'deadline': analysis.get('deadline'),
                'event_duration_minutes': analysis.get('event_duration_minutes', 60),
                'status': 'pending'
            }
            
            return quest_data
            
        except Exception as e:
            logger.error(f"Failed to create quest from analysis: {e}")
            return None
    
    def generate_daily_tasks(self, user_preferences: Dict) -> List[Dict[str, Any]]:
        """Generate daily tasks based on user preferences"""
        try:
            daily_tasks = user_preferences.get('daily_tasks', [])
            generated_quests = []
            
            for task in daily_tasks:
                quest_data = {
                    'email_id': None,  # Daily tasks are not email-based
                    'title': f"Daily: {task}",
                    'description': f"Complete your daily task: {task}",
                    'quest_type': 'daily_task',
                    'quest_category': 'daily',
                    'importance': 'daily',
                    'urgency': 'medium',
                    'deadline': None,  # Daily tasks don't have specific deadlines
                    'event_duration_minutes': 30,  # Default 30 minutes for daily tasks
                    'status': 'pending'
                }
                generated_quests.append(quest_data)
            
            logger.info(f"Generated {len(generated_quests)} daily tasks")
            return generated_quests
            
        except Exception as e:
            logger.error(f"Failed to generate daily tasks: {e}")
            return []

