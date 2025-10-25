#!/usr/bin/env python3
"""
Example Demonstration of Enhanced Leveling System
Shows complete flow: quest completion, rewards, penalties, and recovery
"""
import os
from main_integration import LevelingSystemIntegration


def print_divider(title=""):
    """Print a nice divider"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'-'*60}\n")


def display_user_stats(stats):
    """Display user stats in a nice format"""
    print(f"📊 User Stats:")
    print(f"   Level: {stats.get('current_level', 1)}")
    print(f"   Total XP: {stats.get('total_xp', 0)} / {stats.get('xp_for_next_level', 100)}")
    print(f"   Coins: {stats.get('total_coins', 0)}")
    print(f"   Streak: {stats.get('current_streak', 0)} days (Longest: {stats.get('longest_streak', 0)})")
    print(f"\n   💪 Stats:")
    print(f"      Focus: {stats.get('focus_stat', 0)}")
    print(f"      Stamina: {stats.get('stamina_stat', 0)}")
    print(f"      Discipline: {stats.get('discipline_stat', 0)}")
    print(f"      Intellect: {stats.get('intellect_stat', 0)}")
    print(f"      Creativity: {stats.get('creativity_stat', 0)}")
    print(f"\n   📈 Quests Completed:")
    print(f"      Total: {stats.get('total_quests_completed', 0)}")
    if 'daily_quests_completed' in stats:
        print(f"      Daily: {stats.get('daily_quests_completed', 0)}")
        print(f"      Side: {stats.get('side_quests_completed', 0)}")
        print(f"      Main: {stats.get('main_quests_completed', 0)}")
        print(f"      Workouts: {stats.get('workout_quests_completed', 0)}")


def main():
    """Run the demonstration"""
    print_divider("🎮 SOLO LEVELING - ENHANCED SYSTEM DEMO 🎮")
    
    # Initialize system
    db_path = 'demo_leveling.db'
    if os.path.exists(db_path):
        os.remove(db_path)  # Fresh start
    
    system = LevelingSystemIntegration(db_path)
    user_id = 1
    quest_id = 100
    
    # ==================== DAILY QUEST ====================
    print_divider("DAY 1: Complete Daily Quest")
    print("📝 Quest: Study for 30 minutes")
    print("   Category: daily")
    print("   Difficulty: medium")
    print("   Time: 30 minutes")
    
    result = system.complete_quest(
        user_id=user_id,
        quest_id=quest_id,
        quest_category='daily',
        difficulty='medium',
        time_estimate=30
    )
    quest_id += 1
    
    print(f"\n✅ Quest Complete!")
    print(f"   Base XP: {result['xp_earned']['base_xp']}")
    print(f"   Final XP: {result['xp_earned']['final_xp']}")
    print(f"   Streak Bonus: +{result['xp_earned']['streak_bonus']}")
    
    if result['reward_chest']:
        chest = result['reward_chest']
        print(f"\n🎁 Reward Chest Dropped: {chest['chest_tier'].upper()}")
        if chest.get('restaurant_name'):
            print(f"   {chest['restaurant_name']}: ${chest['estimated_value']:.2f} value")
            print(f"   🔗 {chest['offer_url']}")
    
    print_divider()
    display_user_stats(result['user_stats'])
    
    # ==================== BUILD STREAK ====================
    print_divider("DAYS 2-7: Build Streak")
    
    for day in range(2, 8):
        print(f"\n📅 Day {day}: Complete daily quest...")
        result = system.complete_quest(
            user_id=user_id,
            quest_id=quest_id,
            quest_category='daily',
            difficulty='medium',
            time_estimate=30
        )
        quest_id += 1
        
        print(f"   XP: +{result['xp_earned']['final_xp']} (Streak: {result['streak']['current']} days)")
        if day >= 7:
            print(f"   🔥 Streak bonus active: +{result['xp_earned']['streak_bonus']} XP!")
    
    print_divider()
    display_user_stats(result['user_stats'])
    
    # ==================== SIDE QUEST ====================
    print_divider("DAY 8: Complete Side Quest (Quiz)")
    print("📝 Quest: Complete weekly quiz")
    print("   Category: side")
    print("   Difficulty: hard")
    print("   Time: 90 minutes")
    
    result = system.complete_quest(
        user_id=user_id,
        quest_id=quest_id,
        quest_category='side',
        difficulty='hard',
        time_estimate=90
    )
    quest_id += 1
    
    print(f"\n✅ Quest Complete!")
    print(f"   XP: +{result['xp_earned']['final_xp']}")
    print(f"   Stats Gained:")
    for stat, value in result['stats_gained'].items():
        if value > 0:
            print(f"      {stat.capitalize()}: +{value}")
    
    if result['reward_chest']:
        chest = result['reward_chest']
        print(f"\n🎁 {chest['chest_tier'].upper()} Chest!")
    
    if result['level_up']['leveled_up']:
        print(f"\n🎉 LEVEL UP! New Level: {result['level_up']['new_level']}")
        rewards = result['level_up']['rewards']
        print(f"   Coins: +{rewards['coins']}")
        if rewards.get('special_reward'):
            print(f"   Special Reward: {rewards['special_reward']}")
    
    print_divider()
    display_user_stats(result['user_stats'])
    
    # ==================== WORKOUT ====================
    print_divider("DAY 9: Complete Workout")
    print("🏃 Quest: 45-minute run")
    print("   Category: workout")
    print("   Difficulty: medium")
    print("   Time: 45 minutes")
    print("   Intensity: 7/10")
    
    result = system.complete_quest(
        user_id=user_id,
        quest_id=quest_id,
        quest_category='workout',
        difficulty='medium',
        time_estimate=45,
        intensity_level=7
    )
    quest_id += 1
    
    print(f"\n✅ Workout Complete!")
    print(f"   XP: +{result['xp_earned']['final_xp']}")
    print(f"   Stamina: +{result['stats_gained']['stamina']} 💪")
    
    print_divider()
    display_user_stats(result['user_stats'])
    
    # ==================== MISS A QUEST ====================
    print_divider("DAY 10: Missed Daily Quest")
    print("❌ Oh no! Missed today's daily quest")
    
    penalty_result = system.miss_quest(
        user_id=user_id,
        quest_id=quest_id,
        quest_category='daily',
        quest_xp=20,
        had_partial_progress=False
    )
    quest_id += 1
    
    penalty = penalty_result['penalty']
    print(f"\n⚠️  {penalty['message']}")
    print(f"   XP Lost: {penalty['xp_lost']}")
    print(f"   Old Streak: {penalty['old_streak']} → New Streak: {penalty['new_streak']}")
    
    if penalty.get('rehab_chain'):
        rehab = penalty['rehab_chain']
        print(f"\n🔧 Rehab Available:")
        print(f"   {rehab['description']}")
        print(f"   Progress: {rehab['completed_quests']}/{rehab['required_quests']}")
    
    print_divider()
    display_user_stats(penalty_result['user_stats'])
    
    # ==================== REHAB CHAIN ====================
    print_divider("DAYS 11-13: Rehab Chain")
    print("🔧 Working on streak recovery...")
    
    for day in range(11, 14):
        print(f"\n📅 Day {day}: Rehab quest...")
        result = system.complete_quest(
            user_id=user_id,
            quest_id=quest_id,
            quest_category='daily',
            difficulty='easy',
            time_estimate=20
        )
        quest_id += 1
        
        print(f"   XP: +{result['xp_earned']['final_xp']}")
        print(f"   New Streak: {result['streak']['current']} days")
    
    print(f"\n✅ Rehab chain complete! Streak restored!")
    
    print_divider()
    display_user_stats(result['user_stats'])
    
    # ==================== MAIN QUEST ====================
    print_divider("WEEK 4: Main Quest (Final Exam)")
    print("📚 Quest: Complete final exam")
    print("   Category: main")
    print("   Difficulty: hard")
    print("   Course Weight: 1.5 (important course)")
    
    result = system.complete_quest(
        user_id=user_id,
        quest_id=quest_id,
        quest_category='main',
        difficulty='hard',
        course_weight=1.5
    )
    quest_id += 1
    
    print(f"\n✅ EXAM COMPLETE!")
    print(f"   XP: +{result['xp_earned']['final_xp']} 🎓")
    
    if result['reward_chest']:
        chest = result['reward_chest']
        print(f"\n🎁 {chest['chest_tier'].upper()} CHEST DROPPED!")
        print(f"   Reward Type: {chest['reward_type']}")
        if chest.get('restaurant_name'):
            print(f"   Offer: {chest['restaurant_name']}")
            print(f"   Value: ${chest['estimated_value']:.2f}")
            print(f"   🔗 Link: {chest['offer_url']}")
    
    if result['level_up']['leveled_up']:
        level_up = result['level_up']
        print(f"\n🎉 LEVEL UP! Level {level_up['new_level']}!")
        if level_up['rewards'].get('badge'):
            print(f"   🏅 {level_up['rewards']['badge']}")
        if level_up['rewards'].get('special_reward'):
            print(f"   🎁 Special: {level_up['rewards']['special_reward']}")
    
    print_divider()
    display_user_stats(result['user_stats'])
    
    # ==================== SUMMARY ====================
    print_divider("📊 FINAL SUMMARY")
    
    stats = result['user_stats']
    print(f"🎮 Journey Complete!")
    print(f"\n   Starting → Current:")
    print(f"   Level: 1 → {stats['current_level']}")
    print(f"   XP: 0 → {stats['total_xp']}")
    print(f"   Coins: 0 → {stats['total_coins']}")
    print(f"   Quests: 0 → {stats['total_quests_completed']}")
    print(f"\n   Peak Streak: {stats['longest_streak']} days 🔥")
    print(f"   Total Stat Points: {sum([stats['focus_stat'], stats['stamina_stat'], stats['discipline_stat'], stats['intellect_stat'], stats['creativity_stat']])}")
    
    print(f"\n{'='*60}")
    print(f"  System Features Demonstrated:")
    print(f"{'='*60}")
    print("  ✅ XP calculation & scaling")
    print("  ✅ Level progression")
    print("  ✅ Stat growth")
    print("  ✅ Streak system")
    print("  ✅ Reward chests with real offers")
    print("  ✅ Penalty system")
    print("  ✅ Rehab chains")
    print("  ✅ Multiple quest types")
    print(f"{'='*60}\n")
    
    print(f"💾 Database saved to: {db_path}")
    print(f"📖 See README.md for full documentation")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

