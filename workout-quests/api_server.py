"""
FastAPI server for Workout Quests system.
Mirrors functionality from main.py but as REST API endpoints.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from api.exercises_api_client import ExercisesAPIClient
from services.workout_planner import WorkoutPlanner
from services.quest_manager import QuestManager
from services.leveling_integration import LevelingSystemIntegration
from models.workout_models import (
    UserFitnessLevel,
    UserWorkoutProfile,
    WorkoutQuest,
    QuestStatus
)

app = FastAPI(title="Workout Quests API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (maps user_id to UserWorkoutProfile)
user_profiles: Dict[str, UserWorkoutProfile] = {}

# Initialize services
api_key = os.getenv("API_NINJAS_KEY")
if not api_key:
    print("⚠️  Warning: API_NINJAS_KEY not set. Using demo mode.")
    api_key = "demo_key"

api_client = ExercisesAPIClient(api_key=api_key)
workout_planner = WorkoutPlanner(api_client)

# Find rewards cache
rewards_cache_path = None
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rewards_dir = os.path.join(project_root, "backend-rewards")
if os.path.exists(rewards_dir):
    json_files = [f for f in os.listdir(rewards_dir) 
                 if f.startswith("shopping_offers_") and f.endswith(".json")]
    if json_files:
        json_files.sort(reverse=True)
        rewards_cache_path = os.path.join(rewards_dir, json_files[0])

quest_manager = QuestManager(rewards_cache_path=rewards_cache_path)
leveling_integration = LevelingSystemIntegration()


# Pydantic models for API
class CreateUserRequest(BaseModel):
    user_id: str
    fitness_level: str  # "beginner", "intermediate", "expert"


class GeneratePlanRequest(BaseModel):
    duration_weeks: int = 4


class QuestResponse(BaseModel):
    quest_id: str
    title: str
    description: str
    status: str
    experience_reward: int
    coin_reward: int
    exercises: List[Dict]
    cached_rewards: List[Dict]
    created_at: str


class UserProfileResponse(BaseModel):
    user_id: str
    fitness_level: str
    total_workouts_completed: int
    total_experience_earned: int
    total_coins_earned: int
    active_quests_count: int
    completed_quests_count: int


class StatsResponse(BaseModel):
    user_id: str
    fitness_level: str
    total_workouts: int
    total_xp: int
    total_coins: int
    active_quests: int
    completed_quests: int
    current_plan_days: int


def get_or_create_user(user_id: str, fitness_level: str = "beginner") -> UserWorkoutProfile:
    """Get or create user profile."""
    if user_id not in user_profiles:
        level_map = {
            "beginner": UserFitnessLevel.BEGINNER,
            "intermediate": UserFitnessLevel.INTERMEDIATE,
            "expert": UserFitnessLevel.EXPERT
        }
        user_profiles[user_id] = UserWorkoutProfile(
            user_id=user_id,
            fitness_level=level_map.get(fitness_level.lower(), UserFitnessLevel.BEGINNER)
        )
    return user_profiles[user_id]


def quest_to_response(quest: WorkoutQuest) -> QuestResponse:
    """Convert WorkoutQuest to API response."""
    exercises = [
        {
            "name": ex.name,
            "sets": ex.sets,
            "reps": ex.reps,
            "rest_seconds": ex.rest_seconds,
            "muscle": ex.muscle,
            "equipment": ex.equipment,
            "difficulty": ex.difficulty,
            "instructions": ex.instructions
        }
        for ex in quest.workout_day.exercises
    ]
    
    return QuestResponse(
        quest_id=quest.quest_id,
        title=quest.title,
        description=quest.description,
        status=quest.status.value,
        experience_reward=quest.experience_reward,
        coin_reward=quest.coin_reward,
        exercises=exercises,
        cached_rewards=quest.cached_rewards,
        created_at=quest.created_at.isoformat()
    )


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Workout Quests API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/api/users", response_model=UserProfileResponse)
def create_user(request: CreateUserRequest):
    """Create a new user profile. Maps to: create_user_profile() in main.py"""
    user = get_or_create_user(request.user_id, request.fitness_level)
    
    return UserProfileResponse(
        user_id=user.user_id,
        fitness_level=user.fitness_level.value,
        total_workouts_completed=user.total_workouts_completed,
        total_experience_earned=user.total_experience_earned,
        total_coins_earned=user.total_coins_earned,
        active_quests_count=len(user.active_quests),
        completed_quests_count=len(user.completed_quests)
    )


@app.get("/api/users/{user_id}", response_model=UserProfileResponse)
def get_user(user_id: str):
    """Get user profile. Maps to: get_profile_summary() in main.py"""
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = user_profiles[user_id]
    return UserProfileResponse(
        user_id=user.user_id,
        fitness_level=user.fitness_level.value,
        total_workouts_completed=user.total_workouts_completed,
        total_experience_earned=user.total_experience_earned,
        total_coins_earned=user.total_coins_earned,
        active_quests_count=len(user.active_quests),
        completed_quests_count=len(user.completed_quests)
    )


@app.get("/api/users/{user_id}/stats", response_model=StatsResponse)
def get_user_stats(user_id: str):
    """Get user statistics."""
    if user_id not in user_profiles:
        # Return default stats for new user
        return StatsResponse(
            user_id=user_id,
            fitness_level="beginner",
            total_workouts=0,
            total_xp=0,
            total_coins=0,
            active_quests=0,
            completed_quests=0,
            current_plan_days=0
        )
    
    user = user_profiles[user_id]
    plan_days = len(user.current_plan.workout_days) if user.current_plan else 0
    
    return StatsResponse(
        user_id=user.user_id,
        fitness_level=user.fitness_level.value,
        total_workouts=user.total_workouts_completed,
        total_xp=user.total_experience_earned,
        total_coins=user.total_coins_earned,
        active_quests=len(user.active_quests),
        completed_quests=len(user.completed_quests),
        current_plan_days=plan_days
    )


@app.post("/api/users/{user_id}/workout-plan")
def generate_workout_plan(user_id: str, request: GeneratePlanRequest):
    """
    Generate a workout plan and create quests.
    Maps to: generate_workout_plan_with_quests() in main.py
    """
    user = get_or_create_user(user_id)
    
    # Generate workout plan
    workout_plan = workout_planner.generate_workout_plan(
        user_level=user.fitness_level,
        duration_weeks=request.duration_weeks
    )
    
    if not workout_plan:
        raise HTTPException(status_code=500, detail="Failed to generate workout plan")
    
    user.current_plan = workout_plan
    
    # Create quests from the plan
    quests = quest_manager.create_quests_from_plan(workout_plan)
    
    # Add quests to user profile
    for quest in quests:
        user.add_active_quest(quest)
    
    return {
        "message": "Workout plan generated",
        "plan_id": workout_plan.plan_id,
        "duration_weeks": workout_plan.duration_weeks,
        "days_per_week": workout_plan.days_per_week,
        "total_exercises": workout_plan.get_total_exercises(),
        "quests_created": len(quests)
    }


@app.get("/api/users/{user_id}/quests", response_model=List[QuestResponse])
def get_active_quests(user_id: str):
    """
    Get all active quests for a user.
    Maps to: display_active_quests() in main.py
    """
    if user_id not in user_profiles:
        return []
    
    user = user_profiles[user_id]
    return [quest_to_response(quest) for quest in user.active_quests]


@app.get("/api/users/{user_id}/quests/{quest_id}", response_model=QuestResponse)
def get_quest_details(user_id: str, quest_id: str):
    """
    Get details for a specific quest.
    Maps to: show_quest_details() in main.py
    """
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = user_profiles[user_id]
    
    # Check active quests
    for quest in user.active_quests:
        if quest.quest_id == quest_id:
            return quest_to_response(quest)
    
    # Check completed quests
    for quest in user.completed_quests:
        if quest.quest_id == quest_id:
            return quest_to_response(quest)
    
    raise HTTPException(status_code=404, detail="Quest not found")


@app.post("/api/users/{user_id}/quests/{quest_id}/complete")
def complete_quest(user_id: str, quest_id: str):
    """
    Complete a quest and award rewards.
    Maps to: complete_quest_interactive() in main.py
    """
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = user_profiles[user_id]
    
    # Complete the quest
    completed_quest = quest_manager.complete_quest(user, quest_id)
    
    if not completed_quest:
        raise HTTPException(status_code=404, detail="Quest not found or already completed")
    
    # Award through leveling system if available
    leveling_result = None
    if leveling_integration.is_available():
        rewards = leveling_integration.award_quest_completion(
            user_id=user_id,
            quest=completed_quest
        )
        leveling_result = rewards.get("leveling_system_result")
    
    return {
        "message": "Quest completed!",
        "quest_id": quest_id,
        "rewards": {
            "xp": completed_quest.experience_reward,
            "coins": completed_quest.coin_reward,
            "special_rewards": completed_quest.cached_rewards
        },
        "leveling_result": leveling_result,
        "new_stats": {
            "total_workouts": user.total_workouts_completed,
            "total_xp": user.total_experience_earned,
            "total_coins": user.total_coins_earned
        }
    }


@app.get("/api/users/{user_id}/completed-quests", response_model=List[QuestResponse])
def get_completed_quests(user_id: str):
    """Get all completed quests for a user."""
    if user_id not in user_profiles:
        return []
    
    user = user_profiles[user_id]
    return [quest_to_response(quest) for quest in user.completed_quests]


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting Workout Quests API Server")
    print("="*60)
    print("📝 API Documentation: http://localhost:8000/docs")
    print("🏋️  Frontend: http://localhost:8080/workout-quests")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)

