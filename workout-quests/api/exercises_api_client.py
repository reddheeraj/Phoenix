"""
Client for the Exercises API from api-ninjas.com
Documentation: https://www.api-ninjas.com/api/exercises
"""
import os
import requests
from typing import List, Dict, Optional
from enum import Enum


class ExerciseType(Enum):
    """Exercise types as defined by the API."""
    CARDIO = "cardio"
    OLYMPIC_WEIGHTLIFTING = "olympic_weightlifting"
    PLYOMETRICS = "plyometrics"
    POWERLIFTING = "powerlifting"
    STRENGTH = "strength"
    STRETCHING = "stretching"
    STRONGMAN = "strongman"


class MuscleGroup(Enum):
    """Muscle groups as defined by the API."""
    ABDOMINALS = "abdominals"
    ABDUCTORS = "abductors"
    ADDUCTORS = "adductors"
    BICEPS = "biceps"
    CALVES = "calves"
    CHEST = "chest"
    FOREARMS = "forearms"
    GLUTES = "glutes"
    HAMSTRINGS = "hamstrings"
    LATS = "lats"
    LOWER_BACK = "lower_back"
    MIDDLE_BACK = "middle_back"
    NECK = "neck"
    QUADRICEPS = "quadriceps"
    TRAPS = "traps"
    TRICEPS = "triceps"


class DifficultyLevel(Enum):
    """Difficulty levels as defined by the API."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class ExercisesAPIClient:
    """Client for interacting with the API Ninjas Exercises API."""
    
    BASE_URL = "https://api.api-ninjas.com/v1/exercises"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Exercises API client.
        
        Args:
            api_key: API key for api-ninjas.com. If not provided, will look for
                    API_NINJAS_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("API_NINJAS_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Provide via constructor or set API_NINJAS_KEY env variable."
            )
        
        self.headers = {
            "X-Api-Key": self.api_key
        }
    
    def get_exercises(
        self,
        name: Optional[str] = None,
        exercise_type: Optional[ExerciseType] = None,
        muscle: Optional[MuscleGroup] = None,
        difficulty: Optional[DifficultyLevel] = None,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get exercises matching the specified criteria.
        
        Args:
            name: Name of exercise (partial match supported)
            exercise_type: Type of exercise
            muscle: Target muscle group
            difficulty: Difficulty level
            offset: Number of results to offset for pagination
            
        Returns:
            List of exercise dictionaries containing:
                - name: Exercise name
                - type: Exercise type
                - muscle: Target muscle
                - equipment: Required equipment
                - difficulty: Difficulty level
                - instructions: Exercise instructions
        """
        params = {}
        
        if name:
            params["name"] = name
        if exercise_type:
            params["type"] = exercise_type.value
        if muscle:
            params["muscle"] = muscle.value
        if difficulty:
            params["difficulty"] = difficulty.value
        if offset > 0:
            params["offset"] = offset
        
        try:
            response = requests.get(
                self.BASE_URL,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching exercises: {e}")
            return []
    
    def get_exercises_by_muscle_group(
        self,
        muscle: MuscleGroup,
        difficulty: Optional[DifficultyLevel] = None,
        exercise_type: Optional[ExerciseType] = None
    ) -> List[Dict]:
        """
        Get exercises for a specific muscle group.
        
        Args:
            muscle: Target muscle group
            difficulty: Optional difficulty filter
            exercise_type: Optional exercise type filter
            
        Returns:
            List of exercises
        """
        return self.get_exercises(
            muscle=muscle,
            difficulty=difficulty,
            exercise_type=exercise_type
        )
    
    def get_beginner_exercises(self, muscle: Optional[MuscleGroup] = None) -> List[Dict]:
        """Get beginner-level exercises."""
        return self.get_exercises(muscle=muscle, difficulty=DifficultyLevel.BEGINNER)
    
    def get_intermediate_exercises(self, muscle: Optional[MuscleGroup] = None) -> List[Dict]:
        """Get intermediate-level exercises."""
        return self.get_exercises(muscle=muscle, difficulty=DifficultyLevel.INTERMEDIATE)
    
    def get_expert_exercises(self, muscle: Optional[MuscleGroup] = None) -> List[Dict]:
        """Get expert-level exercises."""
        return self.get_exercises(muscle=muscle, difficulty=DifficultyLevel.EXPERT)

