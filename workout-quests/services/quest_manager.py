"""
Quest manager service for creating and managing workout quests.
"""
import uuid
import json
import os
from typing import List, Dict, Optional
from datetime import datetime

# Handle imports for both package and direct execution
try:
    from ..models.workout_models import (
        WorkoutQuest,
        WorkoutDay,
        WorkoutPlan,
        UserFitnessLevel,
        QuestStatus,
        UserWorkoutProfile
    )
except ImportError:
    from models.workout_models import (
        WorkoutQuest,
        WorkoutDay,
        WorkoutPlan,
        UserFitnessLevel,
        QuestStatus,
        UserWorkoutProfile
    )


class QuestManager:
    """Manages workout quests and rewards."""
    
    # Base rewards for different fitness levels
    REWARD_MULTIPLIERS = {
        UserFitnessLevel.BEGINNER: {"xp": 50, "coins": 10},
        UserFitnessLevel.INTERMEDIATE: {"xp": 100, "coins": 20},
        UserFitnessLevel.EXPERT: {"xp": 200, "coins": 40},
    }
    
    def __init__(self, rewards_cache_path: Optional[str] = None):
        """
        Initialize the quest manager.
        
        Args:
            rewards_cache_path: Path to cached rewards JSON file
        """
        self.rewards_cache_path = rewards_cache_path
        self.cached_rewards = self._load_cached_rewards()
    
    def _load_cached_rewards(self) -> List[Dict]:
        """Load cached rewards from the backend-rewards system."""
        if not self.rewards_cache_path or not os.path.exists(self.rewards_cache_path):
            # Return default rewards if no cache available
            return [
                {
                    "merchant": "Nike",
                    "offer": "20% off fitness gear",
                    "type": "discount",
                    "category": "shopping"
                },
                {
                    "merchant": "Local Gym",
                    "offer": "Free protein shake",
                    "type": "reward",
                    "category": "fitness"
                }
            ]
        
        try:
            with open(self.rewards_cache_path, 'r') as f:
                data = json.load(f)
                # Handle different JSON structures
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'offers' in data:
                    return data['offers']
                else:
                    return []
        except Exception as e:
            print(f"Error loading cached rewards: {e}")
            return []
    
    def _select_rewards(self, count: int = 1) -> List[Dict]:
        """
        Select random rewards from cached rewards.
        
        Args:
            count: Number of rewards to select
            
        Returns:
            List of reward dictionaries
        """
        import random
        if not self.cached_rewards:
            return []
        
        available_count = min(count, len(self.cached_rewards))
        return random.sample(self.cached_rewards, available_count)
    
    def create_quest_from_workout(
        self,
        workout_day: WorkoutDay,
        user_level: UserFitnessLevel,
        quest_title: Optional[str] = None,
        quest_description: Optional[str] = None
    ) -> WorkoutQuest:
        """
        Create a workout quest from a workout day.
        
        Args:
            workout_day: WorkoutDay to convert to a quest
            user_level: User's fitness level for reward calculation
            quest_title: Custom quest title
            quest_description: Custom quest description
            
        Returns:
            WorkoutQuest object
        """
        quest_id = str(uuid.uuid4())
        
        # Generate title and description if not provided
        if not quest_title:
            quest_title = f"{workout_day.focus} Workout Challenge"
        
        if not quest_description:
            exercises_count = len(workout_day.exercises)
            muscles = ", ".join(workout_day.get_target_muscles())
            quest_description = (
                f"Complete a {workout_day.focus.lower()} workout with {exercises_count} exercises "
                f"targeting: {muscles}. Estimated duration: {workout_day.estimated_duration_minutes} minutes."
            )
        
        # Calculate rewards
        multiplier = self.REWARD_MULTIPLIERS[user_level]
        base_xp = multiplier["xp"]
        base_coins = multiplier["coins"]
        
        # Add bonus based on number of exercises
        exercise_bonus = len(workout_day.exercises) * 5
        xp_reward = base_xp + exercise_bonus
        coin_reward = base_coins + (exercise_bonus // 5)
        
        # Select cached rewards
        selected_rewards = self._select_rewards(count=1)
        
        quest = WorkoutQuest(
            quest_id=quest_id,
            title=quest_title,
            description=quest_description,
            workout_day=workout_day,
            experience_reward=xp_reward,
            coin_reward=coin_reward,
            cached_rewards=selected_rewards
        )
        
        return quest
    
    def create_quests_from_plan(
        self,
        workout_plan: WorkoutPlan
    ) -> List[WorkoutQuest]:
        """
        Create multiple quests from a workout plan.
        
        Args:
            workout_plan: WorkoutPlan to convert to quests
            
        Returns:
            List of WorkoutQuest objects
        """
        quests = []
        
        for workout_day in workout_plan.workout_days:
            quest_title = f"Day {workout_day.day_number}: {workout_day.focus}"
            quest = self.create_quest_from_workout(
                workout_day=workout_day,
                user_level=workout_plan.user_level,
                quest_title=quest_title
            )
            quests.append(quest)
        
        return quests
    
    def complete_quest(
        self,
        user_profile: UserWorkoutProfile,
        quest_id: str
    ) -> Optional[WorkoutQuest]:
        """
        Complete a quest for a user.
        
        Args:
            user_profile: User's workout profile
            quest_id: ID of the quest to complete
            
        Returns:
            Completed WorkoutQuest or None if not found
        """
        completed_quest = user_profile.complete_quest(quest_id)
        
        if completed_quest:
            print(f"\n🎉 Quest Completed: {completed_quest.title}")
            print(f"💪 Earned: {completed_quest.experience_reward} XP, {completed_quest.coin_reward} coins")
            
            if completed_quest.cached_rewards:
                print("\n🎁 Special Rewards:")
                for reward in completed_quest.cached_rewards:
                    merchant = reward.get('merchant', reward.get('store', 'Unknown'))
                    offer = reward.get('offer', reward.get('discount', reward.get('deal', 'Special offer')))
                    print(f"  - {merchant}: {offer}")
        
        return completed_quest
    
    def get_active_quests(self, user_profile: UserWorkoutProfile) -> List[WorkoutQuest]:
        """Get all active quests for a user."""
        return user_profile.active_quests
    
    def get_quest_details(self, quest: WorkoutQuest) -> str:
        """
        Get detailed information about a quest.
        
        Args:
            quest: WorkoutQuest object
            
        Returns:
            Formatted string with quest details
        """
        details = f"\n{'='*60}\n"
        details += f"QUEST: {quest.title}\n"
        details += f"{'='*60}\n"
        details += f"Description: {quest.description}\n"
        details += f"Status: {quest.status.value.upper()}\n"
        details += f"\nWorkout Details:\n"
        details += f"  Focus: {quest.workout_day.focus}\n"
        details += f"  Duration: ~{quest.workout_day.estimated_duration_minutes} minutes\n"
        details += f"  Exercises: {len(quest.workout_day.exercises)}\n"
        
        details += f"\nExercises:\n"
        for i, exercise in enumerate(quest.workout_day.exercises, 1):
            details += f"  {i}. {exercise.name}\n"
            details += f"     - Sets: {exercise.sets}x{exercise.reps}\n"
            details += f"     - Muscle: {exercise.muscle.title()}\n"
            details += f"     - Equipment: {exercise.equipment.title()}\n"
            details += f"     - Rest: {exercise.rest_seconds}s\n"
        
        details += f"\nRewards:\n"
        details += f"  💎 {quest.experience_reward} XP\n"
        details += f"  🪙 {quest.coin_reward} Coins\n"
        
        if quest.cached_rewards:
            details += f"\n  🎁 Special Rewards:\n"
            for reward in quest.cached_rewards:
                merchant = reward.get('merchant', reward.get('store', 'Unknown'))
                offer = reward.get('offer', reward.get('discount', reward.get('deal', 'Special offer')))
                details += f"     - {merchant}: {offer}\n"
        
        details += f"{'='*60}\n"
        
        return details

