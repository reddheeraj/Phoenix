"""
Quick demo script showing the workout quest system in action.
Run this to see how the system works without the interactive menu.
"""
import os
from api.exercises_api_client import ExercisesAPIClient, MuscleGroup, DifficultyLevel
from services.workout_planner import WorkoutPlanner
from services.quest_manager import QuestManager
from models.workout_models import UserFitnessLevel, UserWorkoutProfile


def demo_workout_quest_system():
    """Demonstrate the workout quest system."""
    
    print("\n" + "="*60)
    print("🏋️  WORKOUT QUEST SYSTEM - DEMO")
    print("="*60)
    
    # Check for API key
    api_key = os.getenv("API_NINJAS_KEY")
    if not api_key:
        print("\n⚠️  Please set API_NINJAS_KEY environment variable")
        print("Get your free key at: https://www.api-ninjas.com/")
        return
    
    # Initialize components
    print("\n📋 Initializing system...")
    api_client = ExercisesAPIClient(api_key=api_key)
    workout_planner = WorkoutPlanner(api_client)
    
    # Find rewards cache
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    rewards_dir = os.path.join(project_root, "backend-rewards")
    rewards_cache_path = None
    
    if os.path.exists(rewards_dir):
        json_files = [f for f in os.listdir(rewards_dir) 
                     if f.startswith("shopping_offers_") and f.endswith(".json")]
        if json_files:
            json_files.sort(reverse=True)
            rewards_cache_path = os.path.join(rewards_dir, json_files[0])
    
    quest_manager = QuestManager(rewards_cache_path=rewards_cache_path)
    
    print("✅ System initialized")
    
    # Demo 1: Fetch some exercises
    print("\n" + "-"*60)
    print("DEMO 1: Fetching Bicep Exercises")
    print("-"*60)
    
    bicep_exercises = api_client.get_exercises_by_muscle_group(
        muscle=MuscleGroup.BICEPS,
        difficulty=DifficultyLevel.BEGINNER
    )
    
    print(f"Found {len(bicep_exercises)} bicep exercises:")
    for i, exercise in enumerate(bicep_exercises[:3], 1):
        print(f"{i}. {exercise['name']} ({exercise['equipment']})")
    
    # Demo 2: Generate a workout plan
    print("\n" + "-"*60)
    print("DEMO 2: Generating Intermediate Workout Plan")
    print("-"*60)
    
    workout_plan = workout_planner.generate_workout_plan(
        user_level=UserFitnessLevel.INTERMEDIATE,
        duration_weeks=2
    )
    
    print(f"\n{workout_plan.get_plan_summary()}")
    
    # Show first workout day
    if workout_plan.workout_days:
        first_day = workout_plan.workout_days[0]
        print(f"\nDay {first_day.day_number}: {first_day.focus}")
        print(f"Exercises ({len(first_day.exercises)}):")
        for exercise in first_day.exercises[:3]:
            print(f"  - {exercise.name} ({exercise.sets}x{exercise.reps})")
    
    # Demo 3: Create quests
    print("\n" + "-"*60)
    print("DEMO 3: Creating Workout Quests")
    print("-"*60)
    
    quests = quest_manager.create_quests_from_plan(workout_plan)
    print(f"Created {len(quests)} quests from the workout plan")
    
    # Show first quest details
    if quests:
        first_quest = quests[0]
        print(f"\nFirst Quest: {first_quest.title}")
        print(f"Exercises: {len(first_quest.workout_day.exercises)}")
        print(f"Rewards: {first_quest.experience_reward} XP, {first_quest.coin_reward} coins")
        
        if first_quest.cached_rewards:
            print("\nSpecial Rewards:")
            for reward in first_quest.cached_rewards:
                merchant = reward.get('merchant', reward.get('store', 'Unknown'))
                offer = reward.get('offer', reward.get('discount', 'Special offer'))
                print(f"  🎁 {merchant}: {offer}")
    
    # Demo 4: User profile and quest completion
    print("\n" + "-"*60)
    print("DEMO 4: User Profile & Quest Completion")
    print("-"*60)
    
    user_profile = UserWorkoutProfile(
        user_id="demo_user",
        fitness_level=UserFitnessLevel.INTERMEDIATE,
        current_plan=workout_plan
    )
    
    # Add quests to profile
    for quest in quests:
        user_profile.add_active_quest(quest)
    
    print(f"\n{user_profile.get_profile_summary()}")
    
    # Complete first quest
    if quests:
        print(f"\n🎯 Completing first quest...")
        completed = quest_manager.complete_quest(user_profile, quests[0].quest_id)
        
        if completed:
            print(f"\n{user_profile.get_profile_summary()}")
    
    # Demo 5: Exercise recommendations
    print("\n" + "-"*60)
    print("DEMO 5: Exercise Recommendations for Chest")
    print("-"*60)
    
    chest_recommendations = workout_planner.get_exercise_recommendations(
        user_level=UserFitnessLevel.INTERMEDIATE,
        muscle=MuscleGroup.CHEST,
        count=3
    )
    
    print(f"Recommended chest exercises for intermediate level:")
    for i, exercise in enumerate(chest_recommendations, 1):
        print(f"{i}. {exercise.name}")
        print(f"   Sets: {exercise.sets}x{exercise.reps}, Rest: {exercise.rest_seconds}s")
        print(f"   Equipment: {exercise.equipment}")
    
    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)
    print("\nRun 'python main.py' for the full interactive experience!")


if __name__ == "__main__":
    demo_workout_quest_system()

