"""
Integration with the Phoenix leveling system.
"""
import os
import sys
from typing import Optional, Dict

# Handle imports for both package and direct execution
try:
    from ..models.workout_models import UserWorkoutProfile, WorkoutQuest
except ImportError:
    from models.workout_models import UserWorkoutProfile, WorkoutQuest


class LevelingSystemIntegration:
    """Integrates workout quests with the Phoenix leveling system."""
    
    def __init__(self, leveling_system_path: Optional[str] = None):
        """
        Initialize the leveling system integration.
        
        Args:
            leveling_system_path: Path to the leveling system module
        """
        self.leveling_system_path = leveling_system_path or self._get_default_path()
        self.leveling_engine = None
        self.reward_chest_system = None
        
        self._initialize_leveling_system()
    
    def _get_default_path(self) -> str:
        """Get the default path to the leveling system."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        return os.path.join(project_root, "leveling-system")
    
    def _initialize_leveling_system(self):
        """Initialize the leveling system components."""
        try:
            # Add leveling system to Python path
            if self.leveling_system_path not in sys.path:
                sys.path.insert(0, self.leveling_system_path)
            
            from services.leveling_engine import LevelingEngine
            from services.reward_chest_system import RewardChestSystem
            
            self.leveling_engine = LevelingEngine()
            self.reward_chest_system = RewardChestSystem()
            
            print(f"✅ Leveling system integration initialized")
        except ImportError as e:
            print(f"⚠️  Warning: Could not import leveling system: {e}")
            print("   Workout quests will track rewards independently.")
            self.leveling_engine = None
            self.reward_chest_system = None
    
    def award_quest_completion(
        self,
        user_id: str,
        quest: WorkoutQuest
    ) -> Dict:
        """
        Award rewards to user for completing a quest.
        
        Args:
            user_id: User's ID
            quest: Completed WorkoutQuest
            
        Returns:
            Dictionary with reward details
        """
        rewards = {
            "experience": quest.experience_reward,
            "coins": quest.coin_reward,
            "special_rewards": quest.cached_rewards,
            "leveling_system_result": None
        }
        
        if self.leveling_engine:
            try:
                # Award XP through leveling engine
                result = self.leveling_engine.add_experience(
                    user_id=user_id,
                    experience_points=quest.experience_reward,
                    activity_type="workout_quest",
                    description=f"Completed: {quest.title}"
                )
                rewards["leveling_system_result"] = result
                
                # Check if user leveled up and should get reward chest
                if result.get("leveled_up") and self.reward_chest_system:
                    chest_result = self.reward_chest_system.award_level_up_chest(
                        user_id=user_id,
                        new_level=result.get("new_level", 1)
                    )
                    rewards["reward_chest"] = chest_result
                
            except Exception as e:
                print(f"Error awarding through leveling system: {e}")
        
        return rewards
    
    def get_user_level_info(self, user_id: str) -> Optional[Dict]:
        """
        Get user's level information from the leveling system.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dictionary with level info or None
        """
        if not self.leveling_engine:
            return None
        
        try:
            return self.leveling_engine.get_user_level_info(user_id)
        except Exception as e:
            print(f"Error getting user level info: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if leveling system integration is available."""
        return self.leveling_engine is not None

