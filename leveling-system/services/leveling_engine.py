"""
Core Leveling Engine
Handles XP calculations, level progression, and stat growth
"""
import math
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class LevelingEngine:
    """
    Core engine for leveling mechanics
    
    XP Formula: XP_to_next_level = floor(100 * (1.2 ^ current_level))
    """
    
    # XP Base Values by Quest Type
    XP_RANGES = {
        'daily': (10, 25),
        'side': (50, 300),
        'main': (1000, 5000),
        'workout': (20, 200),
        'rehab': (5, 50)
    }
    
    # Stat Distribution by Quest Type (percentage allocation)
    STAT_DISTRIBUTION = {
        'daily': {
            'focus': 30,
            'discipline': 40,
            'stamina': 10,
            'intellect': 10,
            'creativity': 10
        },
        'side': {
            'focus': 20,
            'discipline': 20,
            'stamina': 10,
            'intellect': 40,
            'creativity': 10
        },
        'main': {
            'focus': 25,
            'discipline': 25,
            'stamina': 15,
            'intellect': 25,
            'creativity': 10
        },
        'workout': {
            'focus': 10,
            'discipline': 30,
            'stamina': 50,
            'intellect': 5,
            'creativity': 5
        },
        'rehab': {
            'focus': 20,
            'discipline': 50,
            'stamina': 10,
            'intellect': 10,
            'creativity': 10
        }
    }
    
    def __init__(self):
        pass
    
    def calculate_xp_for_level(self, level: int) -> int:
        """
        Calculate XP required to reach next level
        Formula: floor(100 * (1.2 ^ level))
        """
        return math.floor(100 * (1.2 ** level))
    
    def calculate_quest_xp(
        self, 
        quest_category: str,
        difficulty: str,
        time_estimate: int = 30,
        intensity_level: int = 5,
        course_weight: float = 1.0
    ) -> int:
        """
        Calculate XP for a quest based on multiple factors
        
        Args:
            quest_category: Type of quest (daily, side, main, workout)
            difficulty: easy, medium, hard, extreme
            time_estimate: Estimated time in minutes
            intensity_level: 1-10 scale for workout intensity
            course_weight: Multiplier for academic importance (1.0-2.0)
        
        Returns:
            Calculated XP value
        """
        # Get base range
        min_xp, max_xp = self.XP_RANGES.get(quest_category, (10, 25))
        
        # Difficulty multiplier
        difficulty_multipliers = {
            'easy': 0.7,
            'medium': 1.0,
            'hard': 1.3,
            'extreme': 1.6
        }
        diff_mult = difficulty_multipliers.get(difficulty, 1.0)
        
        # Calculate base XP (average of range)
        base_xp = (min_xp + max_xp) / 2
        
        # Apply multipliers
        if quest_category == 'daily':
            # Daily: scaled by time estimate
            time_factor = time_estimate / 30  # 30 min baseline
            xp = base_xp * time_factor * diff_mult
            
        elif quest_category == 'side':
            # Side: scaled by difficulty and time
            time_factor = time_estimate / 60  # 60 min baseline
            xp = base_xp * time_factor * diff_mult
            
        elif quest_category == 'main':
            # Main: scaled by course weight and difficulty
            xp = base_xp * course_weight * diff_mult
            
        elif quest_category == 'workout':
            # Workout: scaled by intensity and duration
            intensity_factor = intensity_level / 5  # 5 is baseline
            duration_factor = time_estimate / 45  # 45 min baseline
            xp = base_xp * intensity_factor * duration_factor * diff_mult
            
        else:
            xp = base_xp * diff_mult
        
        # Clamp to range
        xp = max(min_xp, min(max_xp, xp))
        
        return int(xp)
    
    def calculate_stat_rewards(
        self,
        quest_category: str,
        xp_earned: int
    ) -> Dict[str, int]:
        """
        Calculate stat points earned from quest completion
        
        Stats are distributed based on quest type
        Total stat points = XP / 10 (scaled)
        """
        # Get distribution for quest type
        distribution = self.STAT_DISTRIBUTION.get(quest_category, self.STAT_DISTRIBUTION['daily'])
        
        # Total stat points to distribute
        total_stat_points = max(1, xp_earned // 10)
        
        # Distribute according to percentages
        stats = {}
        remaining_points = total_stat_points
        
        for stat, percentage in distribution.items():
            points = int((total_stat_points * percentage) / 100)
            stats[stat] = points
            remaining_points -= points
        
        # Add remaining points to primary stat
        if remaining_points > 0:
            primary_stat = max(distribution, key=distribution.get)
            stats[primary_stat] += remaining_points
        
        return stats
    
    def check_level_up(
        self,
        current_xp: int,
        current_level: int,
        xp_for_next: int
    ) -> Tuple[bool, int, int]:
        """
        Check if user leveled up and calculate new level
        
        Returns:
            (leveled_up, new_level, new_xp_required)
        """
        if current_xp < xp_for_next:
            return (False, current_level, xp_for_next)
        
        # Level up!
        new_level = current_level + 1
        new_xp_required = self.calculate_xp_for_level(new_level)
        
        # Check for multiple level ups
        while current_xp >= new_xp_required:
            new_level += 1
            new_xp_required = self.calculate_xp_for_level(new_level)
        
        return (True, new_level, new_xp_required)
    
    def apply_streak_multiplier(self, base_xp: int, streak: int) -> int:
        """
        Apply streak multiplier to XP
        
        Streak bonuses:
        - 3+ days: +5%
        - 7+ days: +10%
        - 14+ days: +15%
        - 30+ days: +25%
        - 60+ days: +40%
        - 100+ days: +50%
        """
        if streak >= 100:
            multiplier = 1.50
        elif streak >= 60:
            multiplier = 1.40
        elif streak >= 30:
            multiplier = 1.25
        elif streak >= 14:
            multiplier = 1.15
        elif streak >= 7:
            multiplier = 1.10
        elif streak >= 3:
            multiplier = 1.05
        else:
            multiplier = 1.0
        
        return int(base_xp * multiplier)
    
    def apply_xp_debuff(self, base_xp: int, debuff_percent: float) -> int:
        """
        Apply XP debuff (temporary penalty)
        
        Args:
            base_xp: Base XP amount
            debuff_percent: Debuff percentage (e.g., 0.05 for -5%)
        
        Returns:
            Reduced XP amount
        """
        reduction = int(base_xp * debuff_percent)
        return max(1, base_xp - reduction)
    
    def calculate_level_up_rewards(self, new_level: int) -> Dict[str, any]:
        """
        Calculate rewards for reaching a new level
        
        Milestone levels (5, 10, 15, 20, 25, 30, 50, 75, 100) get special rewards
        """
        rewards = {
            'coins': new_level * 10,  # Base coin reward
            'stat_boost': False,
            'special_reward': None,
            'badge': None,
            'title': None
        }
        
        # Milestone rewards
        if new_level % 25 == 0:
            rewards['coins'] *= 3
            rewards['stat_boost'] = 10  # 10% boost to all stats
            rewards['title'] = f"Level {new_level} Master"
            rewards['special_reward'] = 'legendary_chest'
            
        elif new_level % 10 == 0:
            rewards['coins'] *= 2
            rewards['stat_boost'] = 5  # 5% boost to all stats
            rewards['badge'] = f"Level {new_level} Badge"
            rewards['special_reward'] = 'gold_chest'
            
        elif new_level % 5 == 0:
            rewards['coins'] = int(rewards['coins'] * 1.5)
            rewards['badge'] = f"Level {new_level} Achievement"
            rewards['special_reward'] = 'silver_chest'
        
        return rewards
    
    def get_quest_category_requirements(self, quest_category: str) -> Dict[str, any]:
        """
        Get recommended requirements for quest category
        """
        requirements = {
            'daily': {
                'recommended_time': 30,
                'max_time': 120,
                'difficulty_distribution': {'easy': 0.3, 'medium': 0.5, 'hard': 0.2},
                'xp_range': self.XP_RANGES['daily']
            },
            'side': {
                'recommended_time': 60,
                'max_time': 240,
                'difficulty_distribution': {'easy': 0.2, 'medium': 0.4, 'hard': 0.4},
                'xp_range': self.XP_RANGES['side']
            },
            'main': {
                'recommended_time': 180,
                'max_time': 600,
                'difficulty_distribution': {'medium': 0.3, 'hard': 0.5, 'extreme': 0.2},
                'xp_range': self.XP_RANGES['main']
            },
            'workout': {
                'recommended_time': 45,
                'max_time': 150,
                'difficulty_distribution': {'easy': 0.2, 'medium': 0.5, 'hard': 0.3},
                'xp_range': self.XP_RANGES['workout']
            }
        }
        
        return requirements.get(quest_category, requirements['daily'])
    
    def calculate_progress_percentage(
        self,
        current_xp: int,
        level: int,
        xp_for_next: int
    ) -> float:
        """
        Calculate progress towards next level as percentage
        """
        # XP at start of current level
        if level == 1:
            xp_at_level_start = 0
        else:
            xp_at_level_start = sum(
                self.calculate_xp_for_level(lvl) for lvl in range(1, level)
            )
        
        # XP needed for current level
        xp_needed_for_level = xp_for_next - xp_at_level_start
        xp_progress = current_xp - xp_at_level_start
        
        if xp_needed_for_level <= 0:
            return 100.0
        
        percentage = (xp_progress / xp_needed_for_level) * 100
        return min(100.0, max(0.0, percentage))


# Example usage and testing
if __name__ == "__main__":
    engine = LevelingEngine()
    
    print("=== Leveling Engine Test ===\n")
    
    # Test XP calculations for different quest types
    print("XP Calculations:")
    print(f"Daily (medium, 30min): {engine.calculate_quest_xp('daily', 'medium', 30)}")
    print(f"Side Quest (hard, 90min): {engine.calculate_quest_xp('side', 'hard', 90)}")
    print(f"Main Quest (hard, weight 1.5): {engine.calculate_quest_xp('main', 'hard', course_weight=1.5)}")
    print(f"Workout (medium, 60min, intensity 7): {engine.calculate_quest_xp('workout', 'medium', 60, intensity_level=7)}\n")
    
    # Test level progression
    print("Level XP Requirements:")
    for level in [1, 5, 10, 20, 30, 50]:
        xp_needed = engine.calculate_xp_for_level(level)
        print(f"Level {level}: {xp_needed} XP needed")
    
    print("\n=== Test Complete ===")

