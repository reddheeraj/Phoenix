#!/usr/bin/env python3
"""
FastAPI backend for the Solo Leveling System.
Provides REST API endpoints and integrates with Agno AgentOS.
"""

import sys
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path (parent of src/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agno.os import AgentOS
from agno.agent import Agent

from src.database.db_manager import DatabaseManager
from src.agent.quest_agent import QuestAgent
from src.gmail.gmail_client import GmailClient
from src.gcalendar.calendar_client import CalendarClient
from scripts.process_emails import EmailProcessor
from src.llm.quest_analyzer import QuestAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
db_manager = DatabaseManager()
quest_agent = QuestAgent(db_manager)
email_processor = EmailProcessor()

# Create FastAPI app
app = FastAPI(
    title="Solo Leveling System API",
    description="Backend API for the Solo Leveling self-improvement system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QuestResponse(BaseModel):
    id: int
    title: str
    description: str
    quest_type: str
    importance: str
    urgency: str
    deadline: Optional[datetime]
    event_duration_minutes: int
    calendar_event_id: Optional[str]
    status: str
    created_at: datetime

class QuestUpdate(BaseModel):
    status: Optional[str] = None

class UserPreferences(BaseModel):
    user_id: str
    daily_tasks: List[str]
    long_term_goals: List[str]

class UserPreferencesUpdate(BaseModel):
    daily_tasks: Optional[List[str]] = None
    long_term_goals: Optional[List[str]] = None

class OnboardingRequest(BaseModel):
    user_id: str
    daily_tasks: List[str]
    long_term_goals: List[str]

class UserStats(BaseModel):
    user_id: str
    level: int
    total_xp: int
    current_xp: int
    quests_completed: int
    daily_quests_completed: int
    email_quests_completed: int
    streak_days: int
    last_activity_date: Optional[str]

class QuestCompletionResponse(BaseModel):
    quest_id: int
    xp_reward: int
    new_level: int
    level_ups: int
    new_total_xp: int
    new_current_xp: int
    streak_days: int
    message: str

class QuestStats(BaseModel):
    total_quests: int
    completed_quests: int
    pending_quests: int
    in_progress_quests: int
    completion_rate: float
    importance_breakdown: Dict[str, int]
    urgency_breakdown: Dict[str, int]

class ProcessingResult(BaseModel):
    emails_processed: int
    quests_created: int
    calendar_events_created: int

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

# Quest endpoints
@app.get("/quests", response_model=List[QuestResponse])
async def get_quests(
    status: Optional[str] = Query(None, description="Filter by status"),
    importance: Optional[str] = Query(None, description="Filter by importance"),
    urgency: Optional[str] = Query(None, description="Filter by urgency")
):
    """Get quests with optional filters"""
    try:
        quests = db_manager.get_quests(status=status, importance=importance, urgency=urgency)
        return [QuestResponse(**quest) for quest in quests]
    except Exception as e:
        logger.error(f"Failed to get quests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quests/{quest_id}", response_model=QuestResponse)
async def get_quest(quest_id: int = Path(..., description="Quest ID")):
    """Get specific quest by ID"""
    try:
        quests = db_manager.get_quests()
        quest = next((q for q in quests if q['id'] == quest_id), None)
        if not quest:
            raise HTTPException(status_code=404, detail="Quest not found")
        return QuestResponse(**quest)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get quest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/quests/{quest_id}")
async def update_quest(
    quest_id: int = Path(..., description="Quest ID"),
    quest_update: QuestUpdate = None
):
    """Update quest status"""
    try:
        if quest_update and quest_update.status:
            db_manager.update_quest_status(quest_id, quest_update.status)
            return {"message": f"Quest {quest_id} updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="No update data provided")
    except Exception as e:
        logger.error(f"Failed to update quest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quests/stats", response_model=QuestStats)
async def get_quest_stats():
    """Get quest statistics"""
    try:
        stats = db_manager.get_quest_stats()
        
        total_quests = sum(stats.get('status', {}).values())
        completed_quests = stats.get('status', {}).get('completed', 0)
        pending_quests = stats.get('status', {}).get('pending', 0)
        in_progress_quests = stats.get('status', {}).get('in_progress', 0)
        
        completion_rate = (completed_quests / total_quests * 100) if total_quests > 0 else 0
        
        return QuestStats(
            total_quests=total_quests,
            completed_quests=completed_quests,
            pending_quests=pending_quests,
            in_progress_quests=in_progress_quests,
            completion_rate=round(completion_rate, 2),
            importance_breakdown=stats.get('importance', {}),
            urgency_breakdown=stats.get('urgency', {})
        )
    except Exception as e:
        logger.error(f"Failed to get quest stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Email processing endpoints
@app.post("/process-emails", response_model=ProcessingResult)
async def process_emails(days: int = Query(7, description="Number of days to process")):
    """Process emails from the last N days"""
    try:
        results = email_processor.process_emails(days=days)
        return ProcessingResult(**results)
    except Exception as e:
        logger.error(f"Failed to process emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint with Agno agent
@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with the quest management agent"""
    try:
        response = quest_agent.chat(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Failed to chat with agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# User onboarding and preferences endpoints
@app.post("/onboarding", response_model=Dict[str, Any])
async def user_onboarding(request: OnboardingRequest):
    """Complete user onboarding with daily tasks and long-term goals"""
    try:
        # Create user preferences
        db_manager.create_user_preferences(
            user_id=request.user_id,
            daily_tasks=request.daily_tasks,
            long_term_goals=request.long_term_goals
        )
        
        # Create user stats for gamification
        db_manager.create_user_stats(request.user_id)
        
        # Generate daily tasks as quests
        quest_analyzer = QuestAnalyzer()
        user_preferences = {
            'daily_tasks': request.daily_tasks,
            'long_term_goals': request.long_term_goals
        }
        
        daily_quests = quest_analyzer.generate_daily_tasks(user_preferences)
        
        # Add daily tasks to database
        daily_quests_created = 0
        for quest_data in daily_quests:
            db_manager.add_quest(
                user_id=request.user_id,
                email_id=quest_data['email_id'],
                title=quest_data['title'],
                description=quest_data['description'],
                quest_type=quest_data['quest_type'],
                quest_category=quest_data['quest_category'],
                importance=quest_data['importance'],
                urgency=quest_data['urgency'],
                deadline=quest_data['deadline'],
                event_duration_minutes=quest_data['event_duration_minutes']
            )
            daily_quests_created += 1
        
        return {
            "message": "User onboarding completed successfully",
            "user_id": request.user_id,
            "daily_quests_created": daily_quests_created,
            "next_step": "Process emails to generate goal-aligned quests"
        }
        
    except Exception as e:
        logger.error(f"Failed to complete user onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/exists")
async def check_user_exists(user_id: str = Path(..., description="User ID")):
    """Check if user exists in the database"""
    try:
        preferences = db_manager.get_user_preferences(user_id)
        return {"exists": preferences is not None}
    except Exception as e:
        logger.error(f"Failed to check user existence: {e}")
        return {"exists": False}

@app.get("/users/{user_id}/preferences", response_model=UserPreferences)
async def get_user_preferences(user_id: str = Path(..., description="User ID")):
    """Get user preferences"""
    try:
        preferences = db_manager.get_user_preferences(user_id)
        if not preferences:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        return UserPreferences(
            user_id=user_id,
            daily_tasks=preferences['daily_tasks'],
            long_term_goals=preferences['long_term_goals']
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/{user_id}/preferences", response_model=Dict[str, Any])
async def update_user_preferences(
    user_id: str = Path(..., description="User ID"),
    preferences: UserPreferencesUpdate = None
):
    """Update user preferences"""
    try:
        success = db_manager.update_user_preferences(
            user_id=user_id,
            daily_tasks=preferences.daily_tasks,
            long_term_goals=preferences.long_term_goals
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        return {
            "message": "User preferences updated successfully",
            "user_id": user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/quests", response_model=List[QuestResponse])
async def get_user_quests(
    user_id: str = Path(..., description="User ID"),
    quest_type: Optional[str] = Query(None, description="Filter by quest type (daily_task, email_based)")
):
    """Get user's quests, optionally filtered by type"""
    try:
        quests = db_manager.get_user_quests(user_id, quest_type=quest_type)
        return [QuestResponse(**quest) for quest in quests]
    except Exception as e:
        logger.error(f"Failed to get user quests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/{user_id}/process-emails", response_model=Dict[str, Any])
async def process_user_emails(
    user_id: str = Path(..., description="User ID"),
    days: int = Query(7, description="Number of days to process emails")
):
    """Process emails for a specific user and generate goal-aligned quests"""
    try:
        # Get user preferences
        user_preferences = db_manager.get_user_preferences(user_id)
        if not user_preferences:
            raise HTTPException(status_code=404, detail="User preferences not found. Complete onboarding first.")
        
        # Initialize email processor with user context
        processor = EmailProcessor()
        
        # Process emails with user preferences
        results = processor.process_emails_for_user(user_id, user_preferences, days=days)
        
        return {
            "message": "Email processing completed",
            "user_id": user_id,
            "emails_processed": results.get('emails_processed', 0),
            "quests_created": results.get('quests_created', 0),
            "daily_quests_created": results.get('daily_quests_created', 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process user emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Gamification endpoints
@app.get("/users/{user_id}/stats", response_model=UserStats)
async def get_user_stats(user_id: str = Path(..., description="User ID")):
    """Get user's gamification stats"""
    try:
        stats = db_manager.get_user_stats(user_id)
        if not stats:
            raise HTTPException(status_code=404, detail="User stats not found. Complete onboarding first.")
        
        return UserStats(**stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/{user_id}/quests/{quest_id}/complete", response_model=QuestCompletionResponse)
async def complete_quest(
    user_id: str = Path(..., description="User ID"),
    quest_id: int = Path(..., description="Quest ID")
):
    """Complete a quest and award XP"""
    try:
        result = db_manager.complete_quest(quest_id, user_id)
        
        # Create celebration message
        message = f"Quest completed! +{result['xp_reward']} XP"
        if result['level_ups'] > 0:
            message += f" 🎉 LEVEL UP! You're now level {result['new_level']}!"
        if result['streak_days'] > 1:
            message += f" 🔥 {result['streak_days']} day streak!"
        
        return QuestCompletionResponse(
            quest_id=result['quest_id'],
            xp_reward=result['xp_reward'],
            new_level=result['new_level'],
            level_ups=result['level_ups'],
            new_total_xp=result['new_total_xp'],
            new_current_xp=result['new_current_xp'],
            streak_days=result['streak_days'],
            message=message
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to complete quest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/leaderboard", response_model=List[Dict[str, Any]])
async def get_leaderboard(
    user_id: str = Path(..., description="User ID"),
    limit: int = Query(10, description="Number of top users to return")
):
    """Get leaderboard of top users by level and XP"""
    try:
        # This would require a more complex query to get all users
        # For now, return the current user's stats
        stats = db_manager.get_user_stats(user_id)
        if not stats:
            raise HTTPException(status_code=404, detail="User stats not found")
        
        return [{
            "user_id": user_id,
            "level": stats['level'],
            "total_xp": stats['total_xp'],
            "quests_completed": stats['quests_completed'],
            "streak_days": stats['streak_days']
        }]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Create AgentOS for advanced agent functionality
def create_agent_os():
    """Create AgentOS instance with quest agent"""
    try:
        agent_os = AgentOS(agents=[quest_agent.get_agent()])
        return agent_os
    except Exception as e:
        logger.error(f"Failed to create AgentOS: {e}")
        return None

# Initialize AgentOS
agent_os = create_agent_os()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

