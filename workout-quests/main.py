"""
Main entry point for the Workout Quests system.
Creates personalized workout plans and side quests with rewards.
"""
import os
import sys
from typing import Optional
from api.exercises_api_client import ExercisesAPIClient, MuscleGroup
from services.workout_planner import WorkoutPlanner
from services.quest_manager import QuestManager
from services.leveling_integration import LevelingSystemIntegration
from models.workout_models import (
    UserFitnessLevel,
    UserWorkoutProfile,
    WorkoutQuest
)


class WorkoutQuestSystem:
    """Main system for managing workout quests."""
    
    def __init__(self, api_key: Optional[str] = None, rewards_cache_path: Optional[str] = None):
        """
        Initialize the workout quest system.
        
        Args:
            api_key: API Ninjas API key
            rewards_cache_path: Path to cached rewards from backend-rewards
        """
        # Initialize API client
        self.api_client = ExercisesAPIClient(api_key=api_key)
        
        # Initialize services
        self.workout_planner = WorkoutPlanner(self.api_client)
        self.quest_manager = QuestManager(rewards_cache_path=rewards_cache_path)
        self.leveling_integration = LevelingSystemIntegration()
        
        print("✅ Workout Quest System initialized")
        if self.leveling_integration.is_available():
            print("✅ Leveling system integration active")
    
    def create_user_profile(self, user_id: str, fitness_level: UserFitnessLevel) -> UserWorkoutProfile:
        """
        Create a new user workout profile.
        
        Args:
            user_id: Unique user identifier
            fitness_level: User's fitness level
            
        Returns:
            UserWorkoutProfile object
        """
        profile = UserWorkoutProfile(
            user_id=user_id,
            fitness_level=fitness_level
        )
        print(f"\n✅ Created profile for user: {user_id}")
        print(f"   Fitness Level: {fitness_level.value.title()}")
        return profile
    
    def generate_workout_plan_with_quests(
        self,
        user_profile: UserWorkoutProfile,
        duration_weeks: int = 4
    ):
        """
        Generate a complete workout plan with quests for a user.
        
        Args:
            user_profile: User's workout profile
            duration_weeks: Duration of the plan in weeks
        """
        print(f"\n🏋️  Generating {duration_weeks}-week workout plan for {user_profile.fitness_level.value} level...")
        
        # Generate workout plan
        workout_plan = self.workout_planner.generate_workout_plan(
            user_level=user_profile.fitness_level,
            duration_weeks=duration_weeks
        )
        
        if not workout_plan:
            print("❌ Failed to generate workout plan")
            return
        
        user_profile.current_plan = workout_plan
        print(f"✅ Generated plan with {len(workout_plan.workout_days)} workout days")
        print(f"   Total exercises: {workout_plan.get_total_exercises()}")
        
        # Create quests from the plan
        print("\n📋 Creating workout quests...")
        quests = self.quest_manager.create_quests_from_plan(workout_plan)
        
        for quest in quests:
            user_profile.add_active_quest(quest)
        
        print(f"✅ Created {len(quests)} workout quests")
        print(f"\n{user_profile.get_profile_summary()}")
    
    def display_active_quests(self, user_profile: UserWorkoutProfile):
        """Display all active quests for a user."""
        active_quests = self.quest_manager.get_active_quests(user_profile)
        
        if not active_quests:
            print("\n📭 No active quests")
            return
        
        print(f"\n📋 Active Quests ({len(active_quests)}):")
        for i, quest in enumerate(active_quests, 1):
            print(f"\n{i}. {quest.title}")
            print(f"   Exercises: {len(quest.workout_day.exercises)}")
            print(f"   Duration: ~{quest.workout_day.estimated_duration_minutes} min")
            print(f"   Rewards: {quest.experience_reward} XP, {quest.coin_reward} coins")
    
    def show_quest_details(self, quest: WorkoutQuest):
        """Show detailed information about a quest."""
        print(self.quest_manager.get_quest_details(quest))
    
    def complete_quest_interactive(self, user_profile: UserWorkoutProfile, quest_index: int):
        """
        Complete a quest interactively.
        
        Args:
            user_profile: User's workout profile
            quest_index: Index of the quest to complete (0-based)
        """
        if quest_index >= len(user_profile.active_quests):
            print("❌ Invalid quest index")
            return
        
        quest = user_profile.active_quests[quest_index]
        
        # Complete the quest
        completed_quest = self.quest_manager.complete_quest(user_profile, quest.quest_id)
        
        if completed_quest and self.leveling_integration.is_available():
            # Award through leveling system
            rewards = self.leveling_integration.award_quest_completion(
                user_id=user_profile.user_id,
                quest=completed_quest
            )
            
            if rewards.get("leveling_system_result"):
                result = rewards["leveling_system_result"]
                if result.get("leveled_up"):
                    print(f"\n🎊 LEVEL UP! New Level: {result.get('new_level')}")


def interactive_menu(system: WorkoutQuestSystem, user_profile: UserWorkoutProfile):
    """Interactive menu for the workout quest system."""
    while True:
        print("\n" + "="*60)
        print("WORKOUT QUEST SYSTEM - MAIN MENU")
        print("="*60)
        print("1. View Active Quests")
        print("2. View Quest Details")
        print("3. Complete a Quest")
        print("4. Generate New Workout Plan")
        print("5. View Profile Summary")
        print("6. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            system.display_active_quests(user_profile)
        
        elif choice == "2":
            system.display_active_quests(user_profile)
            if user_profile.active_quests:
                try:
                    quest_num = int(input("\nEnter quest number to view details: ")) - 1
                    if 0 <= quest_num < len(user_profile.active_quests):
                        system.show_quest_details(user_profile.active_quests[quest_num])
                    else:
                        print("❌ Invalid quest number")
                except ValueError:
                    print("❌ Please enter a valid number")
        
        elif choice == "3":
            system.display_active_quests(user_profile)
            if user_profile.active_quests:
                try:
                    quest_num = int(input("\nEnter quest number to complete: ")) - 1
                    if 0 <= quest_num < len(user_profile.active_quests):
                        confirm = input(f"\nAre you sure you completed this workout? (yes/no): ").strip().lower()
                        if confirm in ['yes', 'y']:
                            system.complete_quest_interactive(user_profile, quest_num)
                        else:
                            print("Quest not completed.")
                    else:
                        print("❌ Invalid quest number")
                except ValueError:
                    print("❌ Please enter a valid number")
        
        elif choice == "4":
            try:
                weeks = int(input("\nEnter duration in weeks (1-12): "))
                if 1 <= weeks <= 12:
                    system.generate_workout_plan_with_quests(user_profile, duration_weeks=weeks)
                else:
                    print("❌ Please enter a value between 1 and 12")
            except ValueError:
                print("❌ Please enter a valid number")
        
        elif choice == "5":
            print(f"\n{user_profile.get_profile_summary()}")
        
        elif choice == "6":
            print("\n👋 Thanks for using the Workout Quest System!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")


def main():
    """Main function to run the workout quest system."""
    print("\n" + "="*60)
    print("🏋️  WELCOME TO THE WORKOUT QUEST SYSTEM 🏋️")
    print("="*60)
    
    # Check for API key
    api_key = os.getenv("API_NINJAS_KEY")
    if not api_key:
        print("\n⚠️  API_NINJAS_KEY environment variable not set!")
        print("Please set your API key from https://www.api-ninjas.com/")
        api_key = input("Enter your API key (or press Enter to exit): ").strip()
        if not api_key:
            print("Exiting...")
            return
    
    # Find rewards cache
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    rewards_dir = os.path.join(project_root, "backend-rewards")
    
    rewards_cache_path = None
    if os.path.exists(rewards_dir):
        # Find the most recent shopping offers JSON
        json_files = [f for f in os.listdir(rewards_dir) if f.startswith("shopping_offers_") and f.endswith(".json")]
        if json_files:
            json_files.sort(reverse=True)
            rewards_cache_path = os.path.join(rewards_dir, json_files[0])
            print(f"✅ Found rewards cache: {json_files[0]}")
    
    # Initialize system
    try:
        system = WorkoutQuestSystem(api_key=api_key, rewards_cache_path=rewards_cache_path)
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return
    
    # Get user information
    print("\n" + "-"*60)
    print("USER SETUP")
    print("-"*60)
    
    user_id = input("Enter your user ID (or press Enter for 'user_1'): ").strip() or "user_1"
    
    print("\nSelect your fitness level:")
    print("1. Beginner (New to working out)")
    print("2. Intermediate (Some experience)")
    print("3. Expert (Advanced fitness level)")
    
    level_choice = input("Enter your choice (1-3): ").strip()
    
    level_map = {
        "1": UserFitnessLevel.BEGINNER,
        "2": UserFitnessLevel.INTERMEDIATE,
        "3": UserFitnessLevel.EXPERT
    }
    
    fitness_level = level_map.get(level_choice, UserFitnessLevel.BEGINNER)
    
    # Create user profile
    user_profile = system.create_user_profile(user_id, fitness_level)
    
    # Generate initial workout plan
    duration = input("\nEnter workout plan duration in weeks (default 4): ").strip()
    try:
        duration_weeks = int(duration) if duration else 4
    except ValueError:
        duration_weeks = 4
    
    system.generate_workout_plan_with_quests(user_profile, duration_weeks=duration_weeks)
    
    # Show first quest details
    if user_profile.active_quests:
        print("\n" + "="*60)
        print("HERE'S YOUR FIRST WORKOUT QUEST!")
        system.show_quest_details(user_profile.active_quests[0])
    
    # Start interactive menu
    input("\nPress Enter to continue to the main menu...")
    interactive_menu(system, user_profile)


if __name__ == "__main__":
    main()

