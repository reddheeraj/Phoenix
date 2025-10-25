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

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agno.os import AgentOS
from agno.agent import Agent

from src.database.db_manager import DatabaseManager
from src.agent.quest_agent import QuestAgent
from src.gmail.gmail_client import GmailClient
from src.calendar.calendar_client import CalendarClient
from scripts.process_emails import EmailProcessor

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

