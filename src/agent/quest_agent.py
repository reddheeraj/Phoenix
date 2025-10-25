import logging
from typing import List, Dict, Any, Optional
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.aws import AwsBedrock
from agno.tools import tool
from src.database.db_manager import DatabaseManager
from src.agent.agent_tools import QuestAgentTools
from src.config.settings import settings

logger = logging.getLogger(__name__)

class QuestAgent:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.agent_tools = QuestAgentTools(db_manager)
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create Agno agent with quest management tools"""
        
        # Create custom tools for the agent
        @tool
        def get_quests(status: str = None, importance: str = None, urgency: str = None) -> str:
            """Get quests with optional filters. Parameters: status (pending/in_progress/completed/failed), importance (daily/weekly/main_quest/side_quest), urgency (low/medium/high/critical)"""
            try:
                quests = self.agent_tools.get_quests(status, importance, urgency)
                if not quests:
                    return "No quests found matching the criteria."
                
                result = f"Found {len(quests)} quests:\n\n"
                for quest in quests:
                    result += f"🎯 **{quest['title']}**\n"
                    result += f"   Type: {quest['quest_type']}\n"
                    result += f"   Importance: {quest['importance']}\n"
                    result += f"   Urgency: {quest['urgency']}\n"
                    result += f"   Status: {quest['status']}\n"
                    if quest.get('deadline'):
                        result += f"   Deadline: {quest['deadline']}\n"
                    result += f"   Description: {quest['description'][:100]}...\n\n"
                
                return result
            except Exception as e:
                return f"Error getting quests: {str(e)}"
        
        @tool
        def get_quest_by_id(quest_id: int) -> str:
            """Get specific quest by ID"""
            try:
                quest = self.agent_tools.get_quest_by_id(quest_id)
                if not quest:
                    return f"Quest with ID {quest_id} not found."
                
                result = f"🎯 **{quest['title']}**\n"
                result += f"   ID: {quest['id']}\n"
                result += f"   Type: {quest['quest_type']}\n"
                result += f"   Importance: {quest['importance']}\n"
                result += f"   Urgency: {quest['urgency']}\n"
                result += f"   Status: {quest['status']}\n"
                if quest.get('deadline'):
                    result += f"   Deadline: {quest['deadline']}\n"
                if quest.get('event_duration_minutes'):
                    result += f"   Duration: {quest['event_duration_minutes']} minutes\n"
                result += f"   Description: {quest['description']}\n"
                if quest.get('calendar_event_id'):
                    result += f"   Calendar Event ID: {quest['calendar_event_id']}\n"
                
                return result
            except Exception as e:
                return f"Error getting quest: {str(e)}"
        
        @tool
        def update_quest_status(quest_id: int, status: str) -> str:
            """Update quest status. Valid statuses: pending, in_progress, completed, failed"""
            try:
                success = self.agent_tools.update_quest_status(quest_id, status)
                if success:
                    return f"Quest {quest_id} status updated to {status}."
                else:
                    return f"Failed to update quest {quest_id}. Invalid status: {status}"
            except Exception as e:
                return f"Error updating quest status: {str(e)}"
        
        @tool
        def get_quest_stats() -> str:
            """Get quest statistics and progress summary"""
            try:
                stats = self.agent_tools.get_quest_progress_summary()
                if not stats:
                    return "No quest statistics available."
                
                result = f"📊 **Quest Progress Summary**\n\n"
                result += f"Total Quests: {stats.get('total_quests', 0)}\n"
                result += f"Completed: {stats.get('completed_quests', 0)}\n"
                result += f"Pending: {stats.get('pending_quests', 0)}\n"
                result += f"In Progress: {stats.get('in_progress_quests', 0)}\n"
                result += f"Completion Rate: {stats.get('completion_rate', 0)}%\n\n"
                
                # Importance breakdown
                importance_breakdown = stats.get('importance_breakdown', {})
                if importance_breakdown:
                    result += "**Importance Breakdown:**\n"
                    for importance, count in importance_breakdown.items():
                        result += f"  {importance.replace('_', ' ').title()}: {count}\n"
                    result += "\n"
                
                # Urgency breakdown
                urgency_breakdown = stats.get('urgency_breakdown', {})
                if urgency_breakdown:
                    result += "**Urgency Breakdown:**\n"
                    for urgency, count in urgency_breakdown.items():
                        result += f"  {urgency.title()}: {count}\n"
                
                return result
            except Exception as e:
                return f"Error getting quest stats: {str(e)}"
        
        @tool
        def get_high_priority_quests() -> str:
            """Get high priority quests (high urgency or main quests)"""
            try:
                quests = self.agent_tools.get_high_priority_quests()
                if not quests:
                    return "No high priority quests found."
                
                result = f"🚨 **High Priority Quests** ({len(quests)} found)\n\n"
                for quest in quests:
                    result += f"🎯 **{quest['title']}**\n"
                    result += f"   ID: {quest['id']}\n"
                    result += f"   Type: {quest['quest_type']}\n"
                    result += f"   Importance: {quest['importance']}\n"
                    result += f"   Urgency: {quest['urgency']}\n"
                    result += f"   Status: {quest['status']}\n"
                    if quest.get('deadline'):
                        result += f"   Deadline: {quest['deadline']}\n"
                    result += "\n"
                
                return result
            except Exception as e:
                return f"Error getting high priority quests: {str(e)}"
        
        @tool
        def get_quests_by_type(quest_type: str) -> str:
            """Get quests by type (assignment, assessment, event, application, interview, presentation, task)"""
            try:
                quests = self.agent_tools.get_quests_by_type(quest_type)
                if not quests:
                    return f"No {quest_type} quests found."
                
                result = f"📋 **{quest_type.title()} Quests** ({len(quests)} found)\n\n"
                for quest in quests:
                    result += f"🎯 **{quest['title']}**\n"
                    result += f"   ID: {quest['id']}\n"
                    result += f"   Status: {quest['status']}\n"
                    result += f"   Importance: {quest['importance']}\n"
                    result += f"   Urgency: {quest['urgency']}\n"
                    if quest.get('deadline'):
                        result += f"   Deadline: {quest['deadline']}\n"
                    result += "\n"
                
                return result
            except Exception as e:
                return f"Error getting quests by type: {str(e)}"
        
        # Create the agent
        agent = Agent(
            name="Quest Master",
            model=AwsBedrock(
                id=settings.BEDROCK_MODEL_ID,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                aws_session_token=settings.AWS_SESSION_TOKEN,
                region_name=settings.AWS_REGION
            ),
            description="A solo leveling quest management assistant that helps you track and manage your quests for self-improvement.",
            instructions=[
                "You are a Quest Master in a solo leveling system. Your role is to help users manage their quests for self-improvement.",
                "You can help users view quests, update quest status, get progress statistics, and find high priority quests.",
                "Always be encouraging and motivating when discussing quest progress.",
                "Use the available tools to provide accurate and helpful information about quests.",
                "When users ask about their progress, provide detailed statistics and encouragement.",
                "Help users prioritize their quests based on importance and urgency levels.",
                "Be friendly and supportive, like a personal quest management coach."
            ],
            tools=[
                get_quests,
                get_quest_by_id,
                update_quest_status,
                get_quest_stats,
                get_high_priority_quests,
                get_quests_by_type
            ],
            db=SqliteDb(db_file="quest_agent.db"),
            add_history_to_context=True,
            add_datetime_to_context=True,
            markdown=True
        )
        
        return agent
    
    def chat(self, message: str) -> str:
        """Chat with the quest agent"""
        try:
            response = self.agent.run(message)
            return response.content
        except Exception as e:
            logger.error(f"Error in quest agent chat: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_agent(self) -> Agent:
        """Get the underlying Agno agent"""
        return self.agent

