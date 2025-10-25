"""
Main Integration Module
Complete leveling system with XP, penalties, and rewards
"""
import sqlite3
import json
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

from models.enhanced_models import (
    EnhancedUserStats,
    EnhancedQuest,
    RewardChest,
    ENHANCED_TABLES_SQL
)
from services.leveling_engine import LevelingEngine
from services.penalty_system import PenaltySystem
from services.reward_chest_system import RewardChestSystem


class LevelingSystemIntegration:
    """
    Complete leveling system integration
    Combines XP calculation, penalties, rewards, and progression
    """
    
    def __init__(self, db_path: str = 'leveling_system.db'):
        self.db_path = db_path
        self.engine = LevelingEngine()
        self.penalty_system = PenaltySystem()
        self.chest_system = RewardChestSystem()
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database with enhanced tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for table_name, sql in ENHANCED_TABLES_SQL.items():
            cursor.execute(sql)
            print(f"✅ Created table: {table_name}")
        
        conn.commit()
        conn.close()
        print("✅ Database initialized\n")
    
    def complete_quest(
        self,
        user_id: int,
        quest_id: int,
        quest_category: str,
        difficulty: str,
        time_estimate: int = 30,
        intensity_level: int = 5,
        course_weight: float = 1.0,
        progress_percent: int = 100
    ) -> Dict:
        """
        Complete a quest and process all rewards, XP, and progression
        
        Returns:
            Complete results including XP gain, level up, stats, and rewards
        """
        # Get user stats
        stats = self._get_user_stats(user_id)
        
        # Calculate base XP
        base_xp = self.engine.calculate_quest_xp(
            quest_category, difficulty, time_estimate,
            intensity_level, course_weight
        )
        
        # Apply streak multiplier
        xp_with_streak = self.engine.apply_streak_multiplier(base_xp, stats.current_streak)
        
        # Apply debuff if active
        debuff_expired, debuff_amount = self.penalty_system.check_debuff_expiry(
            stats.debuff_expires_at
        )
        
        if not debuff_expired:
            final_xp = self.engine.apply_xp_debuff(xp_with_streak, debuff_amount)
        else:
            final_xp = xp_with_streak
            # Clear debuff
            stats.active_xp_debuff = 0.0
            stats.debuff_expires_at = None
        
        # Calculate stat rewards
        stat_rewards = self.engine.calculate_stat_rewards(quest_category, final_xp)
        
        # Update user stats
        stats.total_xp += final_xp
        stats.total_quests_completed += 1
        
        # Update category-specific counts
        if quest_category == 'daily':
            stats.daily_quests_completed += 1
            stats.current_streak += 1
            stats.last_daily_completed = datetime.now()
        elif quest_category == 'side':
            stats.side_quests_completed += 1
        elif quest_category == 'main':
            stats.main_quests_completed += 1
        elif quest_category == 'workout':
            stats.workout_quests_completed += 1
        
        # Update streak
        if stats.current_streak > stats.longest_streak:
            stats.longest_streak = stats.current_streak
        
        # Apply stats
        stats.focus_stat += stat_rewards.get('focus', 0)
        stats.stamina_stat += stat_rewards.get('stamina', 0)
        stats.discipline_stat += stat_rewards.get('discipline', 0)
        stats.intellect_stat += stat_rewards.get('intellect', 0)
        stats.creativity_stat += stat_rewards.get('creativity', 0)
        
        # Check for level up
        leveled_up, new_level, new_xp_required = self.engine.check_level_up(
            stats.total_xp, stats.current_level, stats.xp_for_next_level
        )
        
        level_up_rewards = None
        if leveled_up:
            stats.current_level = new_level
            stats.xp_for_next_level = new_xp_required
            level_up_rewards = self.engine.calculate_level_up_rewards(new_level)
            
            # Apply level up rewards
            stats.total_coins += level_up_rewards['coins']
        
        # Check for reward chest
        chest_data = None
        is_milestone = leveled_up and level_up_rewards and level_up_rewards.get('special_reward')
        
        chest_tier = self.chest_system.determine_chest_tier(
            quest_category, final_xp, is_milestone, stats.current_level if leveled_up else None
        )
        
        if chest_tier and self.chest_system.should_drop_chest(chest_tier):
            chest_data = self.chest_system.generate_reward_chest(
                chest_tier, user_id, quest_id
            )
            self._save_reward_chest(chest_data)
        
        # Save updated stats
        self._save_user_stats(stats)
        
        # Save stat growth history
        self._save_stat_growth(user_id, quest_id, stat_rewards, quest_category)
        
        # Compile results
        results = {
            'success': True,
            'xp_earned': {
                'base_xp': base_xp,
                'with_streak': xp_with_streak,
                'final_xp': final_xp,
                'streak_bonus': xp_with_streak - base_xp,
                'debuff_reduction': xp_with_streak - final_xp if not debuff_expired else 0
            },
            'stats_gained': stat_rewards,
            'user_stats': stats.to_dict(),
            'level_up': {
                'leveled_up': leveled_up,
                'new_level': new_level if leveled_up else stats.current_level,
                'rewards': level_up_rewards
            },
            'reward_chest': chest_data,
            'streak': {
                'current': stats.current_streak,
                'longest': stats.longest_streak
            }
        }
        
        return results
    
    def miss_quest(
        self,
        user_id: int,
        quest_id: int,
        quest_category: str,
        quest_xp: int,
        had_partial_progress: bool = False
    ) -> Dict:
        """
        Process a missed quest with penalties
        
        Returns:
            Penalty details and rehab options
        """
        stats = self._get_user_stats(user_id)
        
        # Calculate penalty based on quest type
        if quest_category == 'daily':
            xp_at_level_start = sum(
                self.engine.calculate_xp_for_level(lvl) 
                for lvl in range(1, stats.current_level)
            )
            penalty = self.penalty_system.calculate_missed_daily_penalty(
                quest_xp, had_partial_progress, stats.current_streak,
                stats.total_xp, xp_at_level_start
            )
        elif quest_category == 'side':
            penalty = self.penalty_system.calculate_missed_side_penalty(
                quest_xp, stats.total_coins
            )
        elif quest_category == 'main':
            penalty = self.penalty_system.calculate_missed_main_penalty(
                quest_xp, stats.total_coins, term_bonus=0
            )
        else:
            penalty = {'penalty_type': 'none', 'message': 'No penalty for this quest type'}
        
        # Apply penalty
        if penalty.get('xp_lost', 0) > 0:
            stats.total_xp = max(0, stats.total_xp - penalty['xp_lost'])
            stats.total_xp_lost += penalty['xp_lost']
        
        if penalty.get('coins_lost', 0) > 0:
            stats.total_coins = max(0, stats.total_coins - penalty['coins_lost'])
        
        if penalty.get('debuff_applied', 0) > 0:
            stats.active_xp_debuff = penalty['debuff_applied']
            stats.debuff_expires_at = penalty.get('debuff_expires_at')
        
        if penalty.get('streak_broken', False):
            stats.current_streak = 0
            stats.streak_multiplier = 1.0
        
        # Save updated stats
        self._save_user_stats(stats)
        
        # Log penalty
        self._save_penalty_log(user_id, quest_id, penalty)
        
        # Create rehab chain if applicable
        if penalty.get('rehab_chain'):
            self._create_rehab_chain(user_id, penalty)
        
        return {
            'success': True,
            'penalty': penalty,
            'user_stats': stats.to_dict()
        }
    
    def _get_user_stats(self, user_id: int) -> EnhancedUserStats:
        """Retrieve user stats from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM user_stats_enhanced WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            row_dict = dict(row)
            # Remove user_id from dict since we pass it as first arg
            row_dict.pop('user_id', None)
            return EnhancedUserStats(user_id, **row_dict)
        else:
            # Create new stats
            stats = EnhancedUserStats(user_id)
            self._save_user_stats(stats)
            return stats
    
    def _save_user_stats(self, stats: EnhancedUserStats):
        """Save user stats to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_stats_enhanced 
            (user_id, total_xp, current_level, xp_for_next_level,
             focus_stat, stamina_stat, discipline_stat, intellect_stat, creativity_stat,
             current_streak, longest_streak, streak_multiplier,
             active_xp_debuff, debuff_expires_at, total_xp_lost,
             total_coins, total_quests_completed,
             daily_quests_completed, side_quests_completed, main_quests_completed, workout_quests_completed,
             last_quest_completed, last_daily_completed, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stats.user_id, stats.total_xp, stats.current_level, stats.xp_for_next_level,
            stats.focus_stat, stats.stamina_stat, stats.discipline_stat, stats.intellect_stat, stats.creativity_stat,
            stats.current_streak, stats.longest_streak, stats.streak_multiplier,
            stats.active_xp_debuff, stats.debuff_expires_at, stats.total_xp_lost,
            stats.total_coins, stats.total_quests_completed,
            stats.daily_quests_completed, stats.side_quests_completed, 
            stats.main_quests_completed, stats.workout_quests_completed,
            datetime.now().isoformat(), getattr(stats, 'last_daily_completed', None),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_reward_chest(self, chest_data: Dict):
        """Save reward chest to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reward_chests
            (user_id, quest_id, chest_tier, reward_data, reward_type,
             restaurant_name, discount_percent, estimated_value, offer_url, promo_code,
             is_opened, expires_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chest_data['user_id'], chest_data['quest_id'], chest_data['chest_tier'],
            chest_data['reward_data'], chest_data['reward_type'],
            chest_data.get('restaurant_name'), chest_data.get('discount_percent'),
            chest_data.get('estimated_value'), chest_data.get('offer_url'),
            chest_data.get('promo_code'), chest_data['is_opened'],
            chest_data['expires_at'], chest_data['created_at']
        ))
        
        conn.commit()
        conn.close()
    
    def _save_stat_growth(self, user_id: int, quest_id: int, stat_rewards: Dict, source: str):
        """Save stat growth history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO stat_growth_history
            (user_id, quest_id, focus_gained, stamina_gained, discipline_gained,
             intellect_gained, creativity_gained, growth_source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, quest_id,
            stat_rewards.get('focus', 0), stat_rewards.get('stamina', 0),
            stat_rewards.get('discipline', 0), stat_rewards.get('intellect', 0),
            stat_rewards.get('creativity', 0), source, datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_penalty_log(self, user_id: int, quest_id: int, penalty: Dict):
        """Save penalty to log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO penalty_log
            (user_id, quest_id, penalty_type, xp_lost, coins_lost,
             debuff_applied, debuff_duration_days, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, quest_id, penalty.get('penalty_type'),
            penalty.get('xp_lost', 0), penalty.get('coins_lost', 0),
            penalty.get('debuff_applied', 0.0), penalty.get('debuff_duration_days', 0),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _create_rehab_chain(self, user_id: int, penalty: Dict):
        """Create a rehab chain for recovery"""
        if not penalty.get('rehab_chain'):
            return
        
        rehab = penalty['rehab_chain']
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get last penalty ID
        cursor.execute("SELECT MAX(id) as penalty_id FROM penalty_log WHERE user_id = ?", (user_id,))
        penalty_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO rehab_chains
            (user_id, penalty_id, chain_type, required_quests, completed_quests,
             xp_to_recover, xp_recovered, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, penalty_id, rehab['chain_type'], rehab['required_quests'],
            rehab['completed_quests'], rehab.get('xp_to_recover', 0),
            rehab.get('xp_recovered', 0), rehab['status'], datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()


# Example usage
if __name__ == "__main__":
    print("=== Leveling System Integration Test ===\n")
    
    system = LevelingSystemIntegration('test_leveling.db')
    
    # Test quest completion
    print("Completing a daily quest...")
    result = system.complete_quest(
        user_id=1,
        quest_id=101,
        quest_category='daily',
        difficulty='medium',
        time_estimate=30
    )
    
    print(f"✅ Quest completed!")
    print(f"   XP Earned: {result['xp_earned']['final_xp']}")
    print(f"   Level: {result['user_stats']['current_level']}")
    print(f"   Current Streak: {result['streak']['current']}")
    if result['reward_chest']:
        print(f"   🎁 Reward Chest: {result['reward_chest']['chest_tier']}")
    
    print("\n=== Test Complete ===")

