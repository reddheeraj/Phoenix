# Quick Start Guide

## Installation

```bash
cd leveling-system
pip install -r requirements.txt
```

## Run the Demo

```bash
python example_demo.py
```

This will run a complete demonstration showing:
- ✅ Daily quest completion with XP and stat growth
- ✅ Streak building (7-day streak = +10% XP bonus)
- ✅ Side quest (quiz) with higher XP rewards
- ✅ Workout tracking with intensity scaling
- ✅ Missed quest penalty and streak break
- ✅ Rehab chain recovery system
- ✅ Main quest (final exam) with massive XP
- ✅ Reward chests with **real restaurant offers**

## Quick API Usage

### Basic Quest Completion

```python
from main_integration import LevelingSystemIntegration

# Initialize
system = LevelingSystemIntegration('my_game.db')

# Complete a daily quest
result = system.complete_quest(
    user_id=1,
    quest_id=101,
    quest_category='daily',  # 'daily', 'side', 'main', 'workout'
    difficulty='medium',     # 'easy', 'medium', 'hard', 'extreme'
    time_estimate=30         # minutes
)

# Check results
print(f"XP Earned: {result['xp_earned']['final_xp']}")
print(f"Level: {result['user_stats']['current_level']}")

# Check for reward chest
if result['reward_chest']:
    chest = result['reward_chest']
    if chest.get('restaurant_name'):
        print(f"🎁 {chest['restaurant_name']}: ${chest['estimated_value']}")
        print(f"Link: {chest['offer_url']}")
```

### Handle Missed Quest

```python
# Process missed quest with penalty
penalty_result = system.miss_quest(
    user_id=1,
    quest_id=102,
    quest_category='daily',
    quest_xp=20,
    had_partial_progress=False
)

print(penalty_result['penalty']['message'])

# Check for rehab option
if penalty_result['penalty'].get('rehab_chain'):
    print("Rehab available to recover!")
```

## Quest Categories

### Daily Quest (10-25 XP)
- Study sessions
- Reading assignments
- Practice problems
- Daily habits

### Side Quest (50-300 XP)
- Quizzes
- Small assignments
- Lab work
- Project milestones

### Main Quest (1000-5000 XP)
- Final exams
- Major projects
- Presentations
- Term papers

### Workout (20-200 XP)
- Gym sessions
- Running/cardio
- Sports practice
- Yoga/stretching

## Reward Chest Tiers

- **Bronze** (60% drop): Daily quest completion → $5+ offers
- **Silver** (80% drop): Side quest / Level 10 → $10+ offers
- **Gold** (90% drop): Main quest → $15+ offers
- **Platinum** (100% drop): Level 25/50/75 → $20+ offers
- **Legendary** (100% drop): Level 100 → $30+ premium offers

## Real Offers Included

The system automatically pulls live deals from:
- McDonald's
- Burger King
- Taco Bell
- Chipotle
- Pizza Hut
- Subway
- KFC
- Domino's
- Arby's
- Sonic
- And more!

## Database

SQLite database is automatically created with all tables:
- `user_stats_enhanced` - User progression and stats
- `quests_enhanced` - Quest tracking
- `penalty_log` - Penalty history
- `rehab_chains` - Recovery progress
- `reward_chests` - Reward inventory
- `stat_growth_history` - Stat tracking
- `level_milestones` - Level rewards

## Key Features

🎮 **XP Formula**: `XP_needed = floor(100 * 1.2^level)`

📊 **5 Stats**: Focus, Stamina, Discipline, Intellect, Creativity

🔥 **Streak Bonuses**:
- 7 days: +10% XP
- 14 days: +15% XP
- 30 days: +25% XP
- 100 days: +50% XP

⚠️ **Mild Penalties**:
- Missed daily: -10% XP (5% if partial), streak reset
- Missed side: Coin loss, -5% XP debuff for 7 days
- Missed main: High coin loss, 20% term bonus loss

🔧 **Rehab Chains**:
- 3 quests → Restore streak
- 5 quests → Recover 75% lost XP
- 4 quests → Remove debuff early

🎁 **Real Rewards**:
- Restaurant coupons with clickable links
- Discount codes
- Value ranges from $5-$30+

## Testing Components

```bash
# Test XP engine
python services/leveling_engine.py

# Test penalty system
python services/penalty_system.py

# Test reward chests
python services/reward_chest_system.py

# Test full integration
python main_integration.py
```

## Next Steps

1. **Integrate with Frontend**: Use the API to power your game UI
2. **Customize XP Ranges**: Edit values in `leveling_engine.py`
3. **Add More Offer Sources**: Extend `reward_chest_system.py`
4. **Create Web API**: Wrap in Flask/FastAPI for HTTP endpoints
5. **Add Authentication**: Connect with user management system

For full documentation, see `README.md`

