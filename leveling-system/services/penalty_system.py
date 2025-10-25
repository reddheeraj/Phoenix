"""
Penalty System - Mild & Recoverable
Handles missed quests, streak breaks, and rehab chains
"""
import math
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta


class PenaltySystem:
    """
    Manages penalties for missed quests with recovery mechanics
    
    Core Principles:
    - Penalties are mild and recoverable
    - Never drop below previous level
    - Provide "rehab" paths to restore progress
    """
    
    # Penalty configurations
    PENALTIES = {
        'missed_daily': {
            'xp_loss_percent': 0.10,  # 10% of quest XP
            'xp_loss_partial': 0.05,  # 5% if partial progress
            'coins_lost': 5,
            'debuff': None,
            'creates_rehab': True
        },
        'missed_side': {
            'xp_loss_percent': 0.0,  # No XP loss
            'coins_lost': 20,
            'debuff': 0.05,  # -5% XP for 7 days
            'debuff_duration_days': 7,
            'creates_rehab': True
        },
        'missed_main': {
            'xp_loss_percent': 0.0,  # No direct XP loss
            'coins_lost': 100,
            'term_bonus_loss': 0.2,  # Lose 20% of accumulated term bonus
            'debuff': None,
            'allow_makeup': True,
            'makeup_xp_reduction': 0.3  # 30% reduced reward
        },
        'streak_break': {
            'xp_loss_percent': 0.0,
            'coins_lost': 0,
            'resets_multiplier': True,
            'creates_rehab': True
        }
    }
    
    # Rehab chain configurations
    REHAB_CHAINS = {
        'streak_recovery': {
            'required_quests': 3,
            'quest_category': 'daily',
            'consecutive_days': True,
            'restores_streak': True
        },
        'xp_recovery': {
            'required_quests': 5,
            'quest_category': 'daily',
            'recovers_xp_percent': 0.75,  # Recover 75% of lost XP
            'bonus_on_complete': 'discipline_boost'
        },
        'debuff_removal': {
            'required_quests': 4,
            'quest_category': 'rehab',
            'removes_debuff': True,
            'bonus_on_complete': 'resilience_badge'
        }
    }
    
    def __init__(self):
        pass
    
    def calculate_missed_daily_penalty(
        self,
        quest_xp: int,
        had_partial_progress: bool = False,
        current_streak: int = 0,
        current_xp: int = 0,
        xp_at_level_start: int = 0
    ) -> Dict:
        """
        Calculate penalty for missing a daily quest
        
        Returns:
            penalty details including XP loss, streak impact, rehab options
        """
        config = self.PENALTIES['missed_daily']
        
        # Calculate XP loss
        loss_percent = config['xp_loss_partial'] if had_partial_progress else config['xp_loss_percent']
        xp_lost = int(quest_xp * loss_percent)
        
        # Soft cap: never lose XP below level start
        actual_xp_lost = min(xp_lost, max(0, current_xp - xp_at_level_start))
        
        # Streak impact
        streak_broken = current_streak > 0
        new_streak = 0 if streak_broken else current_streak
        
        penalty = {
            'penalty_type': 'missed_daily',
            'xp_lost': actual_xp_lost,
            'coins_lost': config['coins_lost'],
            'streak_broken': streak_broken,
            'old_streak': current_streak,
            'new_streak': new_streak,
            'debuff_applied': 0.0,
            'rehab_available': config['creates_rehab'],
            'message': f"Missed daily quest. Lost {actual_xp_lost} XP and streak reset."
        }
        
        if streak_broken:
            penalty['rehab_chain'] = self._create_rehab_chain('streak_recovery', actual_xp_lost)
        
        return penalty
    
    def calculate_missed_side_penalty(
        self,
        quest_xp: int,
        current_coins: int
    ) -> Dict:
        """
        Calculate penalty for missing a side quest (quiz/assignment)
        
        Applies temporary XP debuff and coin penalty
        """
        config = self.PENALTIES['missed_side']
        
        coins_lost = min(config['coins_lost'], current_coins)  # Can't lose more than you have
        debuff = config['debuff']
        debuff_days = config['debuff_duration_days']
        
        penalty = {
            'penalty_type': 'missed_side',
            'xp_lost': 0,
            'coins_lost': coins_lost,
            'debuff_applied': debuff,
            'debuff_duration_days': debuff_days,
            'debuff_expires_at': datetime.now() + timedelta(days=debuff_days),
            'rehab_available': True,
            'message': f"Missed side quest. Lost {coins_lost} coins and -{int(debuff*100)}% XP for {debuff_days} days."
        }
        
        penalty['rehab_chain'] = self._create_rehab_chain('debuff_removal', 0)
        
        return penalty
    
    def calculate_missed_main_penalty(
        self,
        quest_xp: int,
        current_coins: int,
        term_bonus: int = 0
    ) -> Dict:
        """
        Calculate penalty for missing a main quest (final exam)
        
        Higher coin loss and term bonus reduction, but allows makeup quest
        """
        config = self.PENALTIES['missed_main']
        
        coins_lost = min(config['coins_lost'], current_coins)
        term_bonus_lost = int(term_bonus * config['term_bonus_loss'])
        
        # Makeup quest XP (reduced)
        makeup_xp = int(quest_xp * (1 - config['makeup_xp_reduction']))
        
        penalty = {
            'penalty_type': 'missed_main',
            'xp_lost': 0,
            'coins_lost': coins_lost,
            'term_bonus_lost': term_bonus_lost,
            'makeup_available': config['allow_makeup'],
            'makeup_xp': makeup_xp,
            'message': f"Missed main quest. Lost {coins_lost} coins and {term_bonus_lost} term bonus. Makeup available for {makeup_xp} XP."
        }
        
        return penalty
    
    def calculate_streak_break_penalty(
        self,
        current_streak: int,
        streak_multiplier: float
    ) -> Dict:
        """
        Calculate penalty for breaking a streak
        
        Resets multiplier but provides rehab chain to recover
        """
        penalty = {
            'penalty_type': 'streak_break',
            'xp_lost': 0,
            'coins_lost': 0,
            'old_streak': current_streak,
            'new_streak': 0,
            'old_multiplier': streak_multiplier,
            'new_multiplier': 1.0,
            'rehab_available': True,
            'message': f"Streak of {current_streak} days broken. Multiplier reset to 1.0x."
        }
        
        penalty['rehab_chain'] = self._create_rehab_chain('streak_recovery', 0)
        
        return penalty
    
    def _create_rehab_chain(self, chain_type: str, xp_to_recover: int) -> Dict:
        """
        Create a rehab chain configuration
        """
        config = self.REHAB_CHAINS[chain_type]
        
        rehab = {
            'chain_type': chain_type,
            'required_quests': config['required_quests'],
            'completed_quests': 0,
            'xp_to_recover': xp_to_recover,
            'xp_recovered': 0,
            'status': 'active',
            'description': self._get_rehab_description(chain_type),
            'rewards': config.get('bonus_on_complete', 'xp_recovery')
        }
        
        if chain_type == 'streak_recovery':
            rehab['consecutive_days'] = config.get('consecutive_days', True)
            rehab['restores_streak'] = config.get('restores_streak', True)
        elif chain_type == 'xp_recovery':
            rehab['recovery_percent'] = config.get('recovers_xp_percent', 0.75)
        
        return rehab
    
    def _get_rehab_description(self, chain_type: str) -> str:
        """Get user-friendly description of rehab chain"""
        descriptions = {
            'streak_recovery': "Complete 3 daily quests in a row to restore your streak bonus",
            'xp_recovery': "Complete 5 daily quests to recover 75% of lost XP",
            'debuff_removal': "Complete 4 rehab quests to remove XP debuff early"
        }
        return descriptions.get(chain_type, "Complete quests to recover from penalty")
    
    def progress_rehab_chain(
        self,
        rehab_chain: Dict,
        quest_completed: bool = True
    ) -> Dict:
        """
        Progress a rehab chain when quest is completed
        
        Returns updated rehab chain with completion status
        """
        if not quest_completed:
            return rehab_chain
        
        rehab_chain['completed_quests'] += 1
        
        # Check if chain is complete
        if rehab_chain['completed_quests'] >= rehab_chain['required_quests']:
            rehab_chain['status'] = 'completed'
            rehab_chain['completed_at'] = datetime.now().isoformat()
            
            # Calculate recovery
            if rehab_chain['chain_type'] == 'xp_recovery':
                recovery_percent = rehab_chain.get('recovery_percent', 0.75)
                rehab_chain['xp_recovered'] = int(rehab_chain['xp_to_recover'] * recovery_percent)
        
        return rehab_chain
    
    def check_debuff_expiry(
        self,
        debuff_expires_at: Optional[datetime]
    ) -> Tuple[bool, float]:
        """
        Check if debuff has expired
        
        Returns:
            (is_expired, remaining_debuff)
        """
        if not debuff_expires_at:
            return (True, 0.0)
        
        if datetime.now() >= debuff_expires_at:
            return (True, 0.0)
        
        return (False, 0.05)  # Assuming 5% debuff if active
    
    def calculate_forgiveness_factor(
        self,
        user_level: int,
        penalties_received: int,
        quests_completed: int
    ) -> float:
        """
        Calculate forgiveness factor based on user performance
        
        Better overall performance = more lenient penalties
        """
        # Base forgiveness
        forgiveness = 1.0
        
        # Reduce penalties for new users
        if user_level < 5:
            forgiveness *= 0.5
        
        # Reduce penalties for users with good completion rate
        if quests_completed > 0:
            completion_rate = (quests_completed) / (quests_completed + penalties_received)
            if completion_rate > 0.9:
                forgiveness *= 0.7
            elif completion_rate > 0.8:
                forgiveness *= 0.85
        
        return forgiveness


# Example usage
if __name__ == "__main__":
    penalty_system = PenaltySystem()
    
    print("=== Penalty System Test ===\n")
    
    # Test missed daily
    missed_daily = penalty_system.calculate_missed_daily_penalty(
        quest_xp=20,
        had_partial_progress=False,
        current_streak=7,
        current_xp=250,
        xp_at_level_start=200
    )
    print("Missed Daily Quest:")
    print(f"  XP Lost: {missed_daily['xp_lost']}")
    print(f"  Streak Broken: {missed_daily['streak_broken']}")
    print(f"  Rehab Available: {missed_daily['rehab_available']}")
    print(f"  Message: {missed_daily['message']}\n")
    
    # Test missed side quest
    missed_side = penalty_system.calculate_missed_side_penalty(
        quest_xp=100,
        current_coins=50
    )
    print("Missed Side Quest:")
    print(f"  Coins Lost: {missed_side['coins_lost']}")
    print(f"  Debuff: -{int(missed_side['debuff_applied']*100)}% XP")
    print(f"  Duration: {missed_side['debuff_duration_days']} days")
    print(f"  Message: {missed_side['message']}\n")
    
    print("=== Test Complete ===")

