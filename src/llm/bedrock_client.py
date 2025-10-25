import json
import logging
import boto3
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
from src.config.settings import settings

logger = logging.getLogger(__name__)

class BedrockClient:
    def __init__(self):
        self.client = None
        self.model_id = settings.BEDROCK_MODEL_ID
        self.region = settings.AWS_REGION
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AWS Bedrock client"""
        try:
            # Use session token if available (for temporary credentials)
            client_kwargs = {
                'service_name': 'bedrock-runtime',
                'region_name': self.region,
                'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY
            }
            
            # Add session token if it exists (for temporary credentials)
            if hasattr(settings, 'AWS_SESSION_TOKEN') and settings.AWS_SESSION_TOKEN:
                client_kwargs['aws_session_token'] = settings.AWS_SESSION_TOKEN
            
            self.client = boto3.client(**client_kwargs)
            logger.info("Bedrock client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
    
    def generate_quest_analysis(self, email_data: Dict) -> Dict[str, Any]:
        """Generate quest analysis using Claude 3.5 Sonnet"""
        try:
            # Prepare the prompt
            prompt = self._create_quest_analysis_prompt(email_data)
            
            # Prepare the request body
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            # Call Bedrock
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            # Parse the JSON response
            quest_analysis = json.loads(content)
            
            logger.info("Quest analysis generated successfully")
            return quest_analysis
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            # Return default analysis if parsing fails
            return self._get_default_analysis(email_data)
        except Exception as e:
            logger.error(f"Failed to generate quest analysis: {e}")
            raise
    
    def _create_quest_analysis_prompt(self, email_data: Dict) -> str:
        """Create prompt for quest analysis"""
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        sender = email_data.get('sender', '')
        
        prompt = f"""
You are an AI assistant that analyzes emails to create quests for a solo leveling self-improvement system. 

Email Details:
- From: {sender}
- Subject: {subject}
- Body: {body[:2000]}...

Analyze this email and determine if it should become a quest. If it should, provide the following information in JSON format:

{{
    "should_create_quest": true/false,
    "title": "Quest title (if creating quest)",
    "description": "Detailed quest description (if creating quest)",
    "quest_type": "assignment/assessment/event/application/interview/presentation/task",
    "importance": "daily/weekly/main_quest/side_quest",
    "urgency": "low/medium/high/critical",
    "deadline": "YYYY-MM-DD HH:MM:SS or null if no deadline",
    "event_duration_minutes": 60 (default duration in minutes),
    "reasoning": "Brief explanation of the analysis"
}}

Guidelines:
1. Only create quests for actionable items with clear objectives
2. Importance levels:
   - daily: routine tasks, daily habits
   - weekly: weekly goals, recurring tasks
   - main_quest: major assignments, important deadlines
   - side_quest: optional tasks, nice-to-have items
3. Urgency levels:
   - low: can be done anytime
   - medium: should be done soon
   - high: needs attention soon
   - critical: urgent, immediate action required
4. Extract deadlines from email content if mentioned
5. Set appropriate duration based on quest type (default 60 minutes)
6. Be conservative - only create quests for clearly actionable items

Respond with valid JSON only.
"""
        return prompt
    
    def _get_default_analysis(self, email_data: Dict) -> Dict[str, Any]:
        """Get default analysis when LLM fails"""
        return {
            "should_create_quest": False,
            "title": "",
            "description": "",
            "quest_type": "task",
            "importance": "side_quest",
            "urgency": "low",
            "deadline": None,
            "event_duration_minutes": 60,
            "reasoning": "Failed to analyze email content"
        }
    
    def generate_quest_analysis_with_goals(self, email_data: Dict, user_preferences: Dict = None) -> Dict:
        """Generate quest analysis aligned with user's long-term goals"""
        try:
            # Build context with user's long-term goals
            long_term_goals = user_preferences.get('long_term_goals', []) if user_preferences else []
            goals_context = ""
            if long_term_goals:
                goals_context = f"\n\nUser's Long-term Goals: {', '.join(long_term_goals)}"
                goals_context += "\n\nAnalyze if this email content aligns with any of these goals and prioritize quest creation accordingly."
            
            prompt = f"""
Analyze this email and determine if it should become a quest, considering the user's long-term goals.

Email Subject: {email_data.get('subject', 'No subject')}
Email Sender: {email_data.get('sender', 'Unknown sender')}
Email Body: {email_data.get('body', 'No body')[:1000]}...
{goals_context}

Consider:
1. Does this email contain actionable items, deadlines, or important tasks?
2. Does it align with the user's long-term goals?
3. Is it urgent or important enough to become a quest?
4. What type of quest would this be (assignment, event, application, etc.)?

Respond with a JSON object containing:
- should_create_quest: boolean
- title: string (if creating quest)
- description: string (if creating quest)
- quest_type: string (assignment, event, application, interview, task, etc.)
- quest_category: string (work, personal, education, health, etc.)
- importance: string (daily, weekly, main_quest, side_quest)
- urgency: string (low, medium, high, critical)
- deadline: string (ISO format if mentioned, null otherwise)
- event_duration_minutes: integer (estimated duration)
- reasoning: string (explanation of decision and goal alignment)
"""

            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            # Call Bedrock
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            # Try to parse the JSON response
            try:
                quest_analysis = json.loads(content)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    quest_analysis = json.loads(json_match.group(1))
                else:
                    # Try to find JSON object in the content
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        quest_analysis = json.loads(json_match.group(0))
                    else:
                        raise
            
            logger.info("Goal-aligned quest analysis generated successfully")
            return quest_analysis
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

