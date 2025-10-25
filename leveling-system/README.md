# Enhanced Leveling System

A comprehensive gamification system with XP progression, stat growth, mild penalties, and real-world rewards.

## 🎯 Features

### Core Mechanics
- **Dynamic XP System**: XP scales with quest type, difficulty, time, and intensity
- **Level Progression**: Formula-based leveling `XP = floor(100 * 1.2^level)`
- **Multi-Stat Growth**: Focus, Stamina, Discipline, Intellect, Creativity
- **Streak System**: Build streaks for XP multipliers (up to +50% at 100 days)
- **Reward Chests**: Randomized loot with real coupons/discounts

### Quest Categories & XP Ranges

| Quest Type | XP Range | Scaling Factors |
|------------|----------|-----------------|
| Daily Quest | 10-25 XP | Time estimate, difficulty |
| Side Quest (Quiz/Assignment) | 50-300 XP | Time, difficulty |
| Main Quest (Final Exam) | 1000-5000 XP | Course weight, difficulty |
| Workout | 20-200 XP | Intensity, duration |
| Rehab Quest | 5-50 XP | Recovery chain |

### Stat Distribution by Quest Type

Different quest types grant different stat allocations:

- **Daily Quests**: 40% Discipline, 30% Focus, 10% each (Stamina, Intellect, Creativity)
- **Side Quests**: 40% Intellect, 20% Focus, 20% Discipline, 10% each (Stamina, Creativity)
- **Main Quests**: 25% each (Focus, Discipline, Intellect), 15% Stamina, 10% Creativity
- **Workouts**: 50% Stamina, 30% Discipline, 10% Focus, 5% each (Intellect, Creativity)

## 🚫 Penalty System (Mild & Recoverable)

### Missed Daily Quest
- **Penalty**: Lose 10% of quest XP (5% if partial progress)
- **Impact**: Streak breaks, multiplier resets to 1.0x
- **Recovery**: Complete 3-quest rehab chain to restore streak

### Missed Side Quest
- **Penalty**: Lose coins, -5% XP debuff for 7 days
- **Impact**: Temporary morale debuff
- **Recovery**: Complete 4-quest rehab chain to remove debuff early

### Missed Main Quest
- **Penalty**: High coin loss, lose 20% of term bonus
- **Impact**: No direct XP loss
- **Recovery**: Makeup quest available (70% of original XP)

### Safety Nets
- **Level Protection**: Never drop below previous level
- **Soft Caps**: XP loss capped at current level progress
- **Forgiveness**: New users (<level 5) get 50% reduced penalties
- **High Performers**: 90%+ completion rate = 30% reduced penalties

## 🎁 Reward Chest System

### Chest Tiers & Drop Rates

| Tier | Drop Rate | Trigger | Min Value |
|------|-----------|---------|-----------|
| 🥉 Bronze | 60% | Daily quest completion | $5 |
| 🥈 Silver | 80% | Side quest / Level 10 milestone | $10 |
| 🥇 Gold | 90% | Main quest completion | $15 |
| 💎 Platinum | 100% | Level 25, 50, 75 milestones | $20 |
| 👑 Legendary | 100% | Level 100 milestone | $30+ |

### Reward Types
- **Coupons/Discounts**: Real offers from 15+ restaurant chains (McDonald's, Chipotle, Subway, etc.)
- **Coins**: In-app currency (10-500 coins)
- **XP Boosts**: 10-100% XP multiplier for 6-24 hours
- **Gear**: Cosmetic items (badges, avatars, themes, titles)

## 📊 Level Progression

### XP Requirements by Level

| Level | XP Needed | Cumulative XP | Milestone Reward |
|-------|-----------|---------------|------------------|
| 1 → 2 | 100 | 100 | - |
| 5 → 6 | 249 | 1,033 | Silver Chest |
| 10 → 11 | 619 | 4,192 | Gold Chest + Badge |
| 20 → 21 | 3,833 | 40,840 | Gold Chest + Badge |
| 25 → 26 | 7,451 | 78,644 | Platinum Chest + Title |
| 50 → 51 | 910,044 | 18,520,935 | Platinum Chest + Title |
| 100 → 101 | 83,949,541,775 | 1,709,190,755,567 | Legendary Chest + Title |

### Milestone Rewards

- **Level 5**: Silver Chest + Achievement Badge
- **Level 10**: Gold Chest + Badge + 5% stat boost
- **Level 15**: Silver Chest + Achievement Badge
- **Level 20**: Gold Chest + Badge + 5% stat boost
- **Level 25**: Platinum Chest + Title + 10% stat boost + 3x coins
- **Level 50**: Platinum Chest + Title + 10% stat boost + 3x coins

## 🔧 Installation & Setup

```bash
cd leveling-system
pip install -r requirements.txt
```

## 💻 Usage

### Initialize System

```python
from main_integration import LevelingSystemIntegration

# Create leveling system
system = LevelingSystemIntegration('my_leveling.db')
```

### Complete a Quest

```python
# Complete a daily quest
result = system.complete_quest(
    user_id=1,
    quest_id=101,
    quest_category='daily',
    difficulty='medium',
    time_estimate=30  # minutes
)

print(f"XP Earned: {result['xp_earned']['final_xp']}")
print(f"Level: {result['user_stats']['current_level']}")
print(f"Streak: {result['streak']['current']}")

if result['reward_chest']:
    chest = result['reward_chest']
    print(f"Reward: {chest['chest_tier']} chest")
    if chest.get('restaurant_name'):
        print(f"Offer: {chest['restaurant_name']} - ${chest['estimated_value']}")
        print(f"Link: {chest['offer_url']}")
```

### Complete a Side Quest

```python
result = system.complete_quest(
    user_id=1,
    quest_id=102,
    quest_category='side',
    difficulty='hard',
    time_estimate=90  # minutes
)
```

### Complete a Main Quest

```python
result = system.complete_quest(
    user_id=1,
    quest_id=103,
    quest_category='main',
    difficulty='hard',
    course_weight=1.5  # Higher weight for important courses
)
```

### Complete a Workout

```python
result = system.complete_quest(
    user_id=1,
    quest_id=104,
    quest_category='workout',
    difficulty='medium',
    time_estimate=45,  # minutes
    intensity_level=7  # 1-10 scale
)
```

### Handle Missed Quest

```python
penalty_result = system.miss_quest(
    user_id=1,
    quest_id=105,
    quest_category='daily',
    quest_xp=20,
    had_partial_progress=False
)

print(f"Penalty: {penalty_result['penalty']['message']}")
print(f"XP Lost: {penalty_result['penalty']['xp_lost']}")

if penalty_result['penalty'].get('rehab_chain'):
    rehab = penalty_result['penalty']['rehab_chain']
    print(f"Recovery: {rehab['description']}")
```

## 🧪 Testing

### Test Individual Components

```bash
# Test leveling engine
python services/leveling_engine.py

# Test penalty system
python services/penalty_system.py

# Test reward chest system
python services/reward_chest_system.py

# Test full integration
python main_integration.py
```

## 📁 Project Structure

```
leveling-system/
├── models/
│   ├── __init__.py
│   └── enhanced_models.py      # Database models and schemas
├── services/
│   ├── __init__.py
│   ├── leveling_engine.py      # XP calculations and progression
│   ├── penalty_system.py       # Penalty and rehab mechanics
│   └── reward_chest_system.py  # Reward chest and offer integration
├── utils/                       # Utility functions (optional)
├── main_integration.py          # Complete system integration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔗 Integration with Backend

The leveling system is designed to work independently but can be integrated with the main Solo Leveling backend:

1. **Location Finder**: Automatically fetches real offers from `backend-rewards/simple_location_finder.py`
2. **Database**: Can share or sync with backend database
3. **API**: Can be wrapped in API endpoints for frontend consumption

## 🎮 Game Balance

### XP Earning Examples

- Daily: Read 30 pages → 17 XP (medium difficulty)
- Daily: Study 60 minutes → 20 XP (hard difficulty)
- Side: Complete quiz → 100 XP (medium difficulty, 60 min)
- Side: Write essay → 200 XP (hard difficulty, 120 min)
- Main: Final exam → 2000 XP (hard, weight 1.5)
- Workout: 45-min jog → 90 XP (medium, intensity 7)

### Progression Timeline

- **Level 5**: ~1,000 XP (5-7 days of consistent daily quests)
- **Level 10**: ~4,200 XP (3-4 weeks)
- **Level 20**: ~40,800 XP (3-4 months)
- **Level 25**: ~78,600 XP (6-8 months)
- **Level 50**: ~18.5M XP (several years of dedication)

## 🛠️ Customization

### Adjust XP Ranges

Edit `XP_RANGES` in `services/leveling_engine.py`:

```python
XP_RANGES = {
    'daily': (10, 25),    # Increase for harder daily quests
    'side': (50, 300),    # Adjust for your quest difficulty
    'main': (1000, 5000), # Scale with course importance
    'workout': (20, 200)
}
```

### Modify Penalties

Edit `PENALTIES` in `services/penalty_system.py`:

```python
PENALTIES = {
    'missed_daily': {
        'xp_loss_percent': 0.10,  # Change to 0.05 for 5% loss
        # ...
    }
}
```

### Adjust Chest Drop Rates

Edit `CHEST_CONFIG` in `services/reward_chest_system.py`:

```python
'bronze': {
    'drop_rate': 0.60,  # Change to 0.80 for 80% drop rate
    # ...
}
```

## 📝 License

Part of the Solo Leveling project.

## 🤝 Contributing

This leveling system is modular and extensible. To add features:

1. Create new services in `services/`
2. Update database models in `models/enhanced_models.py`
3. Integrate with `main_integration.py`

## 📞 Support

For issues or questions, refer to the main Solo Leveling project documentation.

