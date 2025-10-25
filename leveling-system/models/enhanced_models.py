"""
Enhanced database models for advanced leveling system
Includes stats, penalties, rehab quests, and reward chests
"""
from datetime import datetime
from typing import Dict, Any
import json

# Extended CREATE_TABLES_SQL with new tables
ENHANCED_TABLES_SQL = {
    'user_stats_enhanced': """
        CREATE TABLE IF NOT EXISTS user_stats_enhanced (
            user_id INTEGER PRIMARY KEY,
            total_xp INTEGER DEFAULT 0,
            current_level INTEGER DEFAULT 1,
            xp_for_next_level INTEGER DEFAULT 100,
            
            -- Stats system
            focus_stat INTEGER DEFAULT 0,
            stamina_stat INTEGER DEFAULT 0,
            discipline_stat INTEGER DEFAULT 0,
            intellect_stat INTEGER DEFAULT 0,
            creativity_stat INTEGER DEFAULT 0,
            
            -- Streaks and multipliers
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            streak_multiplier REAL DEFAULT 1.0,
            
            -- Penalties and debuffs
            active_xp_debuff REAL DEFAULT 0.0,
            debuff_expires_at TIMESTAMP NULL,
            total_xp_lost INTEGER DEFAULT 0,
            
            -- Currency and coins
            total_coins INTEGER DEFAULT 0,
            coins_spent INTEGER DEFAULT 0,
            
            -- Completion stats
            total_quests_completed INTEGER DEFAULT 0,
            daily_quests_completed INTEGER DEFAULT 0,
            side_quests_completed INTEGER DEFAULT 0,
            main_quests_completed INTEGER DEFAULT 0,
            workout_quests_completed INTEGER DEFAULT 0,
            
            -- Timestamps
            last_quest_completed TIMESTAMP NULL,
            last_daily_completed TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    'quests_enhanced': """
        CREATE TABLE IF NOT EXISTS quests_enhanced (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            
            -- Quest details
            title TEXT NOT NULL,
            description TEXT,
            quest_category TEXT NOT NULL CHECK(quest_category IN ('daily', 'side', 'main', 'workout', 'rehab')),
            difficulty TEXT DEFAULT 'medium' CHECK(difficulty IN ('easy', 'medium', 'hard', 'extreme')),
            
            -- XP and rewards
            base_xp INTEGER NOT NULL,
            bonus_xp INTEGER DEFAULT 0,
            total_xp INTEGER DEFAULT 0,
            
            -- Stats rewards (JSON format)
            stat_rewards TEXT DEFAULT '{}',
            
            -- Quest metadata
            time_estimate INTEGER DEFAULT 30,
            intensity_level INTEGER DEFAULT 5,
            course_weight REAL DEFAULT 1.0,
            
            -- Status tracking
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'failed', 'expired')),
            progress_percent INTEGER DEFAULT 0,
            
            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP,
            started_at TIMESTAMP NULL,
            completed_at TIMESTAMP NULL,
            
            -- Reward chest flag
            has_reward_chest BOOLEAN DEFAULT FALSE,
            reward_chest_opened BOOLEAN DEFAULT FALSE
        )
    """,
    
    'penalty_log': """
        CREATE TABLE IF NOT EXISTS penalty_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quest_id INTEGER,
            
            penalty_type TEXT NOT NULL CHECK(penalty_type IN ('missed_daily', 'missed_side', 'missed_main', 'streak_break')),
            xp_lost INTEGER DEFAULT 0,
            coins_lost INTEGER DEFAULT 0,
            debuff_applied REAL DEFAULT 0.0,
            debuff_duration_days INTEGER DEFAULT 0,
            
            is_recovered BOOLEAN DEFAULT FALSE,
            recovered_at TIMESTAMP NULL,
            recovery_method TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    'rehab_chains': """
        CREATE TABLE IF NOT EXISTS rehab_chains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            penalty_id INTEGER NOT NULL,
            
            chain_type TEXT NOT NULL CHECK(chain_type IN ('streak_recovery', 'xp_recovery', 'debuff_removal')),
            required_quests INTEGER NOT NULL,
            completed_quests INTEGER DEFAULT 0,
            
            xp_to_recover INTEGER DEFAULT 0,
            xp_recovered INTEGER DEFAULT 0,
            
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'abandoned')),
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP NULL
        )
    """,
    
    'reward_chests': """
        CREATE TABLE IF NOT EXISTS reward_chests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quest_id INTEGER NOT NULL,
            
            chest_tier TEXT NOT NULL CHECK(chest_tier IN ('bronze', 'silver', 'gold', 'platinum', 'legendary')),
            
            -- Reward contents (JSON)
            reward_data TEXT NOT NULL,
            reward_type TEXT NOT NULL CHECK(reward_type IN ('coupon', 'discount', 'gear', 'coins', 'xp_boost')),
            
            -- Offer details from location finder
            restaurant_name TEXT,
            discount_percent REAL,
            estimated_value REAL,
            offer_url TEXT,
            promo_code TEXT,
            
            -- Status
            is_opened BOOLEAN DEFAULT FALSE,
            opened_at TIMESTAMP NULL,
            is_claimed BOOLEAN DEFAULT FALSE,
            claimed_at TIMESTAMP NULL,
            expires_at TIMESTAMP,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    'stat_growth_history': """
        CREATE TABLE IF NOT EXISTS stat_growth_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quest_id INTEGER,
            
            focus_gained INTEGER DEFAULT 0,
            stamina_gained INTEGER DEFAULT 0,
            discipline_gained INTEGER DEFAULT 0,
            intellect_gained INTEGER DEFAULT 0,
            creativity_gained INTEGER DEFAULT 0,
            
            growth_source TEXT NOT NULL,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    'level_milestones': """
        CREATE TABLE IF NOT EXISTS level_milestones (
            level INTEGER PRIMARY KEY,
            xp_required INTEGER NOT NULL,
            
            -- Milestone rewards
            reward_title TEXT,
            reward_description TEXT,
            bonus_coins INTEGER DEFAULT 0,
            stat_boost_percent REAL DEFAULT 0.0,
            
            -- Special unlocks
            unlocks_feature TEXT,
            badge_name TEXT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
}


class EnhancedUserStats:
    """Enhanced user statistics with full stat system"""
    
    def __init__(self, user_id: int, **kwargs):
        self.user_id = user_id
        self.total_xp = kwargs.get('total_xp', 0)
        self.current_level = kwargs.get('current_level', 1)
        self.xp_for_next_level = kwargs.get('xp_for_next_level', 100)
        
        # Stats
        self.focus_stat = kwargs.get('focus_stat', 0)
        self.stamina_stat = kwargs.get('stamina_stat', 0)
        self.discipline_stat = kwargs.get('discipline_stat', 0)
        self.intellect_stat = kwargs.get('intellect_stat', 0)
        self.creativity_stat = kwargs.get('creativity_stat', 0)
        
        # Streaks
        self.current_streak = kwargs.get('current_streak', 0)
        self.longest_streak = kwargs.get('longest_streak', 0)
        self.streak_multiplier = kwargs.get('streak_multiplier', 1.0)
        
        # Penalties
        self.active_xp_debuff = kwargs.get('active_xp_debuff', 0.0)
        self.debuff_expires_at = kwargs.get('debuff_expires_at')
        self.total_xp_lost = kwargs.get('total_xp_lost', 0)
        
        # Currency
        self.total_coins = kwargs.get('total_coins', 0)
        self.coins_spent = kwargs.get('coins_spent', 0)
        
        # Completion stats
        self.total_quests_completed = kwargs.get('total_quests_completed', 0)
        self.daily_quests_completed = kwargs.get('daily_quests_completed', 0)
        self.side_quests_completed = kwargs.get('side_quests_completed', 0)
        self.main_quests_completed = kwargs.get('main_quests_completed', 0)
        self.workout_quests_completed = kwargs.get('workout_quests_completed', 0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'total_xp': self.total_xp,
            'current_level': self.current_level,
            'xp_for_next_level': self.xp_for_next_level,
            'focus_stat': self.focus_stat,
            'stamina_stat': self.stamina_stat,
            'discipline_stat': self.discipline_stat,
            'intellect_stat': self.intellect_stat,
            'creativity_stat': self.creativity_stat,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'streak_multiplier': self.streak_multiplier,
            'active_xp_debuff': self.active_xp_debuff,
            'total_coins': self.total_coins,
            'total_quests_completed': self.total_quests_completed
        }


class EnhancedQuest:
    """Enhanced quest model with XP system and stat rewards"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.title = kwargs.get('title')
        self.description = kwargs.get('description')
        self.quest_category = kwargs.get('quest_category', 'daily')
        self.difficulty = kwargs.get('difficulty', 'medium')
        
        self.base_xp = kwargs.get('base_xp', 10)
        self.bonus_xp = kwargs.get('bonus_xp', 0)
        self.total_xp = kwargs.get('total_xp', self.base_xp)
        
        self.stat_rewards = kwargs.get('stat_rewards', '{}')
        self.time_estimate = kwargs.get('time_estimate', 30)
        self.intensity_level = kwargs.get('intensity_level', 5)
        self.course_weight = kwargs.get('course_weight', 1.0)
        
        self.status = kwargs.get('status', 'pending')
        self.progress_percent = kwargs.get('progress_percent', 0)
        
        self.has_reward_chest = kwargs.get('has_reward_chest', False)
        self.reward_chest_opened = kwargs.get('reward_chest_opened', False)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'quest_category': self.quest_category,
            'difficulty': self.difficulty,
            'base_xp': self.base_xp,
            'total_xp': self.total_xp,
            'status': self.status,
            'has_reward_chest': self.has_reward_chest
        }


class RewardChest:
    """Reward chest model with location-based offers"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.quest_id = kwargs.get('quest_id')
        self.chest_tier = kwargs.get('chest_tier', 'bronze')
        
        self.reward_data = kwargs.get('reward_data', '{}')
        self.reward_type = kwargs.get('reward_type')
        
        self.restaurant_name = kwargs.get('restaurant_name')
        self.discount_percent = kwargs.get('discount_percent')
        self.estimated_value = kwargs.get('estimated_value')
        self.offer_url = kwargs.get('offer_url')
        self.promo_code = kwargs.get('promo_code')
        
        self.is_opened = kwargs.get('is_opened', False)
        self.is_claimed = kwargs.get('is_claimed', False)
        self.expires_at = kwargs.get('expires_at')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'chest_tier': self.chest_tier,
            'reward_type': self.reward_type,
            'restaurant_name': self.restaurant_name,
            'discount_percent': self.discount_percent,
            'estimated_value': self.estimated_value,
            'offer_url': self.offer_url,
            'promo_code': self.promo_code,
            'is_opened': self.is_opened,
            'is_claimed': self.is_claimed
        }

