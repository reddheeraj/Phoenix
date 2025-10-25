# 🏋️ Workout Quests System

Creates personalized workout side quests from the API Ninjas Exercises API and rewards users with XP, coins, and offers from the cached backend-rewards system.

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Get API key from https://www.api-ninjas.com/
export API_NINJAS_KEY="your_key_here"

# 3. Run
python main.py
```

## Features

- 🎯 Personalized workout plans (Beginner/Intermediate/Expert)
- 📋 Side quests with XP, coins, and special rewards
- 🔗 Integrates with Phoenix leveling system
- 🎁 Uses cached rewards from backend-rewards

## Usage

### Interactive Mode
```bash
python main.py  # Full CLI menu
```

### Demo Mode
```bash
python demo.py  # Quick demo
```

### Programmatic
```python
from api.exercises_api_client import ExercisesAPIClient
from services.workout_planner import WorkoutPlanner
from services.quest_manager import QuestManager
from models.workout_models import UserFitnessLevel

# Initialize
client = ExercisesAPIClient(api_key="your_key")
planner = WorkoutPlanner(client)
quest_manager = QuestManager()

# Generate workout plan
plan = planner.generate_workout_plan(
    user_level=UserFitnessLevel.INTERMEDIATE,
    duration_weeks=4
)

# Create quests
quests = quest_manager.create_quests_from_plan(plan)
```

## Structure

```
workout-quests/
├── api/exercises_api_client.py    # API Ninjas client
├── models/workout_models.py       # Data models
├── services/
│   ├── workout_planner.py         # Plan generator
│   ├── quest_manager.py           # Quest system
│   └── leveling_integration.py    # Phoenix integration
└── main.py                        # Interactive CLI
```

## Workout Splits

- **Beginner**: 3-day full body (3x10)
- **Intermediate**: 4-day upper/lower (4x12)
- **Expert**: 5-day body part split (5x15)

## Rewards

Base rewards by level:
- Beginner: 50 XP + 10 coins
- Intermediate: 100 XP + 20 coins
- Expert: 200 XP + 40 coins

Bonus: +5 XP per exercise

## Troubleshooting

**No API key**: Get free key at https://www.api-ninjas.com/  
**No rewards cache**: System uses defaults (backend-rewards optional)  
**No leveling system**: Works standalone (integration optional)

---

Part of the Phoenix Project

