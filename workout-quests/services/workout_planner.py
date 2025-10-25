"""
Workout plan generator service.
Creates personalized workout plans based on user fitness level.
"""
import uuid
from typing import List, Dict, Optional

# Handle imports for both package and direct execution
try:
    from ..api.exercises_api_client import (
        ExercisesAPIClient,
        MuscleGroup,
        DifficultyLevel,
        ExerciseType
    )
    from ..models.workout_models import (
        WorkoutPlan,
        WorkoutDay,
        Exercise,
        UserFitnessLevel
    )
except ImportError:
    from api.exercises_api_client import (
        ExercisesAPIClient,
        MuscleGroup,
        DifficultyLevel,
        ExerciseType
    )
    from models.workout_models import (
        WorkoutPlan,
        WorkoutDay,
        Exercise,
        UserFitnessLevel
    )


class WorkoutPlanner:
    """Service for generating personalized workout plans."""
    
    # Define workout splits for different levels
    BEGINNER_SPLIT = [
        {"day": 1, "focus": "Full Body", "muscles": [MuscleGroup.CHEST, MuscleGroup.BICEPS, MuscleGroup.QUADRICEPS]},
        {"day": 2, "focus": "Full Body", "muscles": [MuscleGroup.MIDDLE_BACK, MuscleGroup.TRICEPS, MuscleGroup.HAMSTRINGS]},
        {"day": 3, "focus": "Full Body", "muscles": [MuscleGroup.ABDOMINALS, MuscleGroup.GLUTES, MuscleGroup.CALVES]},
    ]
    
    INTERMEDIATE_SPLIT = [
        {"day": 1, "focus": "Upper Body Push", "muscles": [MuscleGroup.CHEST, MuscleGroup.TRICEPS, MuscleGroup.ABDOMINALS]},
        {"day": 2, "focus": "Lower Body", "muscles": [MuscleGroup.QUADRICEPS, MuscleGroup.HAMSTRINGS, MuscleGroup.CALVES, MuscleGroup.GLUTES]},
        {"day": 3, "focus": "Upper Body Pull", "muscles": [MuscleGroup.LATS, MuscleGroup.MIDDLE_BACK, MuscleGroup.BICEPS]},
        {"day": 4, "focus": "Full Body", "muscles": [MuscleGroup.CHEST, MuscleGroup.QUADRICEPS, MuscleGroup.ABDOMINALS]},
    ]
    
    EXPERT_SPLIT = [
        {"day": 1, "focus": "Chest & Triceps", "muscles": [MuscleGroup.CHEST, MuscleGroup.TRICEPS]},
        {"day": 2, "focus": "Back & Biceps", "muscles": [MuscleGroup.LATS, MuscleGroup.MIDDLE_BACK, MuscleGroup.BICEPS]},
        {"day": 3, "focus": "Legs", "muscles": [MuscleGroup.QUADRICEPS, MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES, MuscleGroup.CALVES]},
        {"day": 4, "focus": "Shoulders & Abs", "muscles": [MuscleGroup.TRAPS, MuscleGroup.ABDOMINALS]},
        {"day": 5, "focus": "Power & Conditioning", "muscles": [MuscleGroup.CHEST, MuscleGroup.QUADRICEPS, MuscleGroup.LATS]},
    ]
    
    def __init__(self, api_client: ExercisesAPIClient):
        """
        Initialize the workout planner.
        
        Args:
            api_client: Initialized Exercises API client
        """
        self.api_client = api_client
    
    def _get_difficulty_for_level(self, level: UserFitnessLevel) -> DifficultyLevel:
        """Map user fitness level to API difficulty level."""
        mapping = {
            UserFitnessLevel.BEGINNER: DifficultyLevel.BEGINNER,
            UserFitnessLevel.INTERMEDIATE: DifficultyLevel.INTERMEDIATE,
            UserFitnessLevel.EXPERT: DifficultyLevel.EXPERT,
        }
        return mapping[level]
    
    def _get_split_for_level(self, level: UserFitnessLevel) -> List[Dict]:
        """Get workout split for user level."""
        if level == UserFitnessLevel.BEGINNER:
            return self.BEGINNER_SPLIT
        elif level == UserFitnessLevel.INTERMEDIATE:
            return self.INTERMEDIATE_SPLIT
        else:
            return self.EXPERT_SPLIT
    
    def _get_sets_and_reps(self, level: UserFitnessLevel) -> tuple:
        """Get recommended sets and reps for user level."""
        if level == UserFitnessLevel.BEGINNER:
            return (3, 10)  # 3 sets of 10 reps
        elif level == UserFitnessLevel.INTERMEDIATE:
            return (4, 12)  # 4 sets of 12 reps
        else:
            return (5, 15)  # 5 sets of 15 reps
    
    def _create_exercise_from_api_data(
        self,
        api_data: Dict,
        sets: int,
        reps: int
    ) -> Exercise:
        """Create an Exercise object from API response data."""
        return Exercise(
            name=api_data["name"],
            type=api_data["type"],
            muscle=api_data["muscle"],
            equipment=api_data["equipment"],
            difficulty=api_data["difficulty"],
            instructions=api_data["instructions"],
            sets=sets,
            reps=reps,
            rest_seconds=60 if api_data["difficulty"] == "beginner" else 90
        )
    
    def generate_workout_plan(
        self,
        user_level: UserFitnessLevel,
        duration_weeks: int = 4
    ) -> Optional[WorkoutPlan]:
        """
        Generate a complete workout plan for a user.
        
        Args:
            user_level: User's fitness level
            duration_weeks: Duration of the plan in weeks
            
        Returns:
            WorkoutPlan object or None if generation fails
        """
        plan_id = str(uuid.uuid4())
        split = self._get_split_for_level(user_level)
        difficulty = self._get_difficulty_for_level(user_level)
        sets, reps = self._get_sets_and_reps(user_level)
        
        plan = WorkoutPlan(
            plan_id=plan_id,
            user_level=user_level,
            duration_weeks=duration_weeks,
            days_per_week=len(split),
            description=f"{user_level.value.title()} {duration_weeks}-week workout plan"
        )
        
        # Generate workout days
        for day_config in split:
            workout_day = WorkoutDay(
                day_number=day_config["day"],
                focus=day_config["focus"],
                estimated_duration_minutes=30 + (user_level.value == "expert") * 30
            )
            
            # Fetch exercises for each muscle group
            for muscle in day_config["muscles"]:
                exercises = self.api_client.get_exercises_by_muscle_group(
                    muscle=muscle,
                    difficulty=difficulty
                )
                
                # Add 1-2 exercises per muscle group
                exercises_to_add = min(2, len(exercises))
                for i in range(exercises_to_add):
                    if i < len(exercises):
                        exercise = self._create_exercise_from_api_data(
                            exercises[i],
                            sets,
                            reps
                        )
                        workout_day.add_exercise(exercise)
            
            plan.add_workout_day(workout_day)
        
        return plan
    
    def generate_single_workout(
        self,
        user_level: UserFitnessLevel,
        focus: str = "Full Body",
        target_muscles: Optional[List[MuscleGroup]] = None
    ) -> Optional[WorkoutDay]:
        """
        Generate a single workout day.
        
        Args:
            user_level: User's fitness level
            focus: Focus of the workout (e.g., "Upper Body")
            target_muscles: List of muscles to target
            
        Returns:
            WorkoutDay object or None if generation fails
        """
        difficulty = self._get_difficulty_for_level(user_level)
        sets, reps = self._get_sets_and_reps(user_level)
        
        if not target_muscles:
            # Default to a balanced full-body workout
            target_muscles = [
                MuscleGroup.CHEST,
                MuscleGroup.MIDDLE_BACK,
                MuscleGroup.QUADRICEPS,
                MuscleGroup.ABDOMINALS
            ]
        
        workout_day = WorkoutDay(
            day_number=1,
            focus=focus,
            estimated_duration_minutes=45
        )
        
        for muscle in target_muscles:
            exercises = self.api_client.get_exercises_by_muscle_group(
                muscle=muscle,
                difficulty=difficulty
            )
            
            if exercises:
                exercise = self._create_exercise_from_api_data(
                    exercises[0],
                    sets,
                    reps
                )
                workout_day.add_exercise(exercise)
        
        return workout_day
    
    def get_exercise_recommendations(
        self,
        user_level: UserFitnessLevel,
        muscle: MuscleGroup,
        count: int = 3
    ) -> List[Exercise]:
        """
        Get exercise recommendations for a specific muscle group.
        
        Args:
            user_level: User's fitness level
            muscle: Target muscle group
            count: Number of exercises to return
            
        Returns:
            List of Exercise objects
        """
        difficulty = self._get_difficulty_for_level(user_level)
        sets, reps = self._get_sets_and_reps(user_level)
        
        exercises_data = self.api_client.get_exercises_by_muscle_group(
            muscle=muscle,
            difficulty=difficulty
        )
        
        exercises = []
        for i in range(min(count, len(exercises_data))):
            exercise = self._create_exercise_from_api_data(
                exercises_data[i],
                sets,
                reps
            )
            exercises.append(exercise)
        
        return exercises

