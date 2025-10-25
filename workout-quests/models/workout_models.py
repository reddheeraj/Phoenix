"""
Data models for workout plans and quests.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class UserFitnessLevel(Enum):
    """User fitness levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class QuestStatus(Enum):
    """Status of a workout quest."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class Exercise:
    """Represents a single exercise."""
    name: str
    type: str
    muscle: str
    equipment: str
    difficulty: str
    instructions: str
    sets: int = 3
    reps: int = 10
    rest_seconds: int = 60
    
    def __str__(self):
        return f"{self.name} ({self.difficulty}) - {self.sets}x{self.reps}"


@dataclass
class WorkoutDay:
    """Represents a single workout day."""
    day_number: int
    focus: str  # e.g., "Upper Body", "Lower Body", "Full Body"
    exercises: List[Exercise] = field(default_factory=list)
    estimated_duration_minutes: int = 45
    
    def add_exercise(self, exercise: Exercise):
        """Add an exercise to this workout day."""
        self.exercises.append(exercise)
    
    def get_target_muscles(self) -> List[str]:
        """Get list of all muscles targeted in this workout."""
        return list(set(ex.muscle for ex in self.exercises))


@dataclass
class WorkoutPlan:
    """Represents a complete workout plan."""
    plan_id: str
    user_level: UserFitnessLevel
    duration_weeks: int
    days_per_week: int
    workout_days: List[WorkoutDay] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    description: str = ""
    
    def add_workout_day(self, workout_day: WorkoutDay):
        """Add a workout day to the plan."""
        self.workout_days.append(workout_day)
    
    def get_total_exercises(self) -> int:
        """Get total number of exercises in the plan."""
        return sum(len(day.exercises) for day in self.workout_days)
    
    def get_plan_summary(self) -> str:
        """Get a summary of the workout plan."""
        total_exercises = self.get_total_exercises()
        return (
            f"Workout Plan ({self.user_level.value.title()})\n"
            f"Duration: {self.duration_weeks} weeks, {self.days_per_week} days/week\n"
            f"Total Exercises: {total_exercises}\n"
            f"Workout Days: {len(self.workout_days)}"
        )


@dataclass
class WorkoutQuest:
    """Represents a workout side quest."""
    quest_id: str
    title: str
    description: str
    workout_day: WorkoutDay
    status: QuestStatus = QuestStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    experience_reward: int = 0
    coin_reward: int = 0
    cached_rewards: List[Dict] = field(default_factory=list)
    
    def complete_quest(self):
        """Mark the quest as completed."""
        self.status = QuestStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def fail_quest(self):
        """Mark the quest as failed."""
        self.status = QuestStatus.FAILED
    
    def get_quest_summary(self) -> str:
        """Get a summary of the quest."""
        exercises_count = len(self.workout_day.exercises)
        return (
            f"Quest: {self.title}\n"
            f"Description: {self.description}\n"
            f"Exercises: {exercises_count}\n"
            f"Status: {self.status.value}\n"
            f"Rewards: {self.experience_reward} XP, {self.coin_reward} coins"
        )


@dataclass
class UserWorkoutProfile:
    """Represents a user's workout profile."""
    user_id: str
    fitness_level: UserFitnessLevel
    current_plan: Optional[WorkoutPlan] = None
    active_quests: List[WorkoutQuest] = field(default_factory=list)
    completed_quests: List[WorkoutQuest] = field(default_factory=list)
    total_workouts_completed: int = 0
    total_experience_earned: int = 0
    total_coins_earned: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_active_quest(self, quest: WorkoutQuest):
        """Add an active quest to the user's profile."""
        self.active_quests.append(quest)
    
    def complete_quest(self, quest_id: str):
        """Complete a quest and move it to completed quests."""
        for quest in self.active_quests:
            if quest.quest_id == quest_id:
                quest.complete_quest()
                self.active_quests.remove(quest)
                self.completed_quests.append(quest)
                self.total_workouts_completed += 1
                self.total_experience_earned += quest.experience_reward
                self.total_coins_earned += quest.coin_reward
                return quest
        return None
    
    def get_profile_summary(self) -> str:
        """Get a summary of the user's workout profile."""
        return (
            f"User Profile\n"
            f"Fitness Level: {self.fitness_level.value.title()}\n"
            f"Active Quests: {len(self.active_quests)}\n"
            f"Completed Workouts: {self.total_workouts_completed}\n"
            f"Total XP Earned: {self.total_experience_earned}\n"
            f"Total Coins Earned: {self.total_coins_earned}"
        )

