"""
Reward Chest System
Randomized loot with real offers from location-based finder
"""
import random
import json
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Add backend-rewards to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend-rewards'))

try:
    from simple_location_finder import SimpleLocationFinder
except ImportError:
    SimpleLocationFinder = None


class RewardChestSystem:
    """
    Manages reward chests with real-world offers
    
    Chest Tiers:
    - Bronze: Daily quest completion
    - Silver: Side quest completion or milestone
    - Gold: Main quest completion
    - Platinum: Large milestones (level 25, 50, etc.)
    - Legendary: Ultimate achievements (level 100)
    """
    
    # Chest drop rates and configurations
    CHEST_CONFIG = {
        'bronze': {
            'drop_rate': 0.60,  # 60% chance on daily completion
            'reward_types': {
                'coupon': 0.50,
                'coins': 0.30,
                'xp_boost': 0.20
            },
            'coin_range': (10, 30),
            'xp_boost_range': (1.1, 1.15),  # 10-15% boost
            'min_offer_value': 5.0
        },
        'silver': {
            'drop_rate': 0.80,
            'reward_types': {
                'discount': 0.50,
                'coins': 0.25,
                'xp_boost': 0.15,
                'gear': 0.10
            },
            'coin_range': (30, 75),
            'xp_boost_range': (1.15, 1.25),
            'min_offer_value': 10.0
        },
        'gold': {
            'drop_rate': 0.90,
            'reward_types': {
                'coupon': 0.40,
                'discount': 0.30,
                'gear': 0.20,
                'coins': 0.10
            },
            'coin_range': (75, 150),
            'xp_boost_range': (1.25, 1.40),
            'min_offer_value': 15.0
        },
        'platinum': {
            'drop_rate': 1.0,
            'reward_types': {
                'discount': 0.40,
                'coupon': 0.35,
                'gear': 0.25
            },
            'coin_range': (150, 300),
            'xp_boost_range': (1.40, 1.60),
            'min_offer_value': 20.0
        },
        'legendary': {
            'drop_rate': 1.0,
            'reward_types': {
                'discount': 0.45,
                'coupon': 0.35,
                'gear': 0.20
            },
            'coin_range': (300, 500),
            'xp_boost_range': (1.50, 2.0),
            'min_offer_value': 30.0
        }
    }
    
    def __init__(self):
        self.location_finder = SimpleLocationFinder() if SimpleLocationFinder else None
        self._cached_offers = None
        self._cache_timestamp = None
        self._cache_duration = timedelta(hours=12)  # Refresh cache every 12 hours
    
    def should_drop_chest(self, chest_tier: str) -> bool:
        """
        Determine if a chest should drop based on tier drop rate
        """
        config = self.CHEST_CONFIG.get(chest_tier, self.CHEST_CONFIG['bronze'])
        return random.random() < config['drop_rate']
    
    def determine_chest_tier(
        self,
        quest_category: str,
        quest_xp: int,
        is_milestone: bool = False,
        milestone_level: Optional[int] = None
    ) -> Optional[str]:
        """
        Determine chest tier based on quest completion
        """
        # Legendary for major milestones
        if milestone_level and milestone_level >= 100:
            return 'legendary'
        
        # Platinum for significant milestones
        if is_milestone and milestone_level and milestone_level % 25 == 0:
            return 'platinum'
        
        # Gold for main quests
        if quest_category == 'main':
            return 'gold'
        
        # Silver for side quests or level-10 milestones
        if quest_category == 'side' or (is_milestone and milestone_level and milestone_level % 10 == 0):
            return 'silver'
        
        # Bronze for daily and workout
        if quest_category in ['daily', 'workout', 'rehab']:
            return 'bronze'
        
        return None
    
    def _get_cached_offers(self) -> List[Dict]:
        """
        Get cached offers or fetch new ones
        """
        now = datetime.now()
        
        # Check if cache is valid
        if (self._cached_offers and 
            self._cache_timestamp and 
            now - self._cache_timestamp < self._cache_duration):
            return self._cached_offers
        
        # Fetch new offers
        if self.location_finder:
            try:
                print("🔍 Fetching fresh offers from location finder...")
                offers = self.location_finder.find_all_chain_deals()
                self._cached_offers = offers
                self._cache_timestamp = now
                print(f"✅ Cached {len(offers)} offers")
                return offers
            except Exception as e:
                print(f"⚠️ Error fetching offers: {e}")
                return self._cached_offers or []
        
        return []
    
    def _select_offer(self, chest_tier: str) -> Optional[Dict]:
        """
        Select an appropriate offer based on chest tier
        """
        offers = self._get_cached_offers()
        
        if not offers:
            return None
        
        config = self.CHEST_CONFIG[chest_tier]
        min_value = config['min_offer_value']
        
        # Filter offers by minimum value
        suitable_offers = [
            offer for offer in offers 
            if offer.get('estimated_value', 0) >= min_value
        ]
        
        if not suitable_offers:
            suitable_offers = offers  # Fallback to all offers
        
        # Select random offer
        return random.choice(suitable_offers)
    
    def generate_reward_chest(
        self,
        chest_tier: str,
        user_id: int,
        quest_id: int
    ) -> Dict:
        """
        Generate a reward chest with random loot
        
        Returns chest data with rewards
        """
        config = self.CHEST_CONFIG.get(chest_tier, self.CHEST_CONFIG['bronze'])
        
        # Determine reward type
        reward_type = self._roll_reward_type(config['reward_types'])
        
        # Generate reward based on type
        if reward_type in ['coupon', 'discount']:
            reward_data = self._generate_offer_reward(chest_tier, reward_type)
        elif reward_type == 'coins':
            reward_data = self._generate_coin_reward(config)
        elif reward_type == 'xp_boost':
            reward_data = self._generate_xp_boost(config)
        elif reward_type == 'gear':
            reward_data = self._generate_gear_reward(chest_tier)
        else:
            reward_data = self._generate_coin_reward(config)  # Fallback
        
        chest = {
            'user_id': user_id,
            'quest_id': quest_id,
            'chest_tier': chest_tier,
            'reward_type': reward_type,
            'reward_data': json.dumps(reward_data),
            'is_opened': False,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        # Add offer-specific fields if applicable
        if reward_type in ['coupon', 'discount'] and reward_data.get('offer'):
            offer = reward_data['offer']
            chest.update({
                'restaurant_name': offer.get('restaurant'),
                'discount_percent': offer.get('discount_percent'),
                'estimated_value': offer.get('estimated_value'),
                'offer_url': offer.get('url'),
                'promo_code': self._extract_promo_code(offer.get('title', ''))
            })
        
        return chest
    
    def _roll_reward_type(self, reward_weights: Dict[str, float]) -> str:
        """
        Roll for reward type based on weighted probabilities
        """
        roll = random.random()
        cumulative = 0.0
        
        for reward_type, weight in reward_weights.items():
            cumulative += weight
            if roll <= cumulative:
                return reward_type
        
        # Fallback
        return list(reward_weights.keys())[0]
    
    def _generate_offer_reward(self, chest_tier: str, reward_type: str) -> Dict:
        """
        Generate reward with real offer from location finder
        """
        offer = self._select_offer(chest_tier)
        
        if not offer:
            # Fallback to generic reward
            return {
                'type': reward_type,
                'description': f'Generic {reward_type} - Check local deals!',
                'value': 10.0
            }
        
        return {
            'type': reward_type,
            'offer': offer,
            'description': offer.get('title', 'Special Offer'),
            'restaurant': offer.get('restaurant'),
            'value': offer.get('estimated_value', 10.0),
            'url': offer.get('url'),
            'terms': offer.get('terms', ''),
            'verified': offer.get('verified_live', False)
        }
    
    def _generate_coin_reward(self, config: Dict) -> Dict:
        """
        Generate coin reward
        """
        min_coins, max_coins = config['coin_range']
        coins = random.randint(min_coins, max_coins)
        
        return {
            'type': 'coins',
            'amount': coins,
            'description': f'{coins} bonus coins!',
            'value': coins / 10  # Rough dollar equivalent
        }
    
    def _generate_xp_boost(self, config: Dict) -> Dict:
        """
        Generate XP boost reward
        """
        min_boost, max_boost = config['xp_boost_range']
        boost = round(random.uniform(min_boost, max_boost), 2)
        duration_hours = random.choice([6, 12, 24])
        
        return {
            'type': 'xp_boost',
            'multiplier': boost,
            'duration_hours': duration_hours,
            'description': f'{int((boost-1)*100)}% XP boost for {duration_hours} hours',
            'expires_at': (datetime.now() + timedelta(hours=duration_hours)).isoformat()
        }
    
    def _generate_gear_reward(self, chest_tier: str) -> Dict:
        """
        Generate cosmetic gear reward
        """
        gear_types = ['badge', 'avatar', 'theme', 'title', 'banner']
        rarities = {'bronze': 'common', 'silver': 'uncommon', 'gold': 'rare', 
                   'platinum': 'epic', 'legendary': 'legendary'}
        
        gear_type = random.choice(gear_types)
        rarity = rarities.get(chest_tier, 'common')
        
        gear_names = {
            'badge': ['Achiever', 'Champion', 'Scholar', 'Warrior', 'Master'],
            'avatar': ['Crown', 'Wings', 'Aura', 'Halo', 'Shadow'],
            'theme': ['Dark Mode', 'Neon', 'Forest', 'Ocean', 'Fire'],
            'title': ['The Dedicated', 'The Persistent', 'The Achiever', 'The Legend'],
            'banner': ['Victory', 'Excellence', 'Mastery', 'Glory']
        }
        
        name = random.choice(gear_names.get(gear_type, ['Special']))
        
        return {
            'type': 'gear',
            'gear_type': gear_type,
            'name': f'{rarity.capitalize()} {name}',
            'rarity': rarity,
            'description': f'Unlock the {name} {gear_type}',
            'equipped': False
        }
    
    def _extract_promo_code(self, title: str) -> Optional[str]:
        """
        Extract promo code from offer title if present
        """
        import re
        match = re.search(r'\(Code:\s*([A-Z0-9]+)\)', title)
        if match:
            return match.group(1)
        return None
    
    def open_chest(self, chest: Dict) -> Dict:
        """
        Open a chest and reveal rewards
        """
        if chest.get('is_opened'):
            return {
                'success': False,
                'message': 'Chest already opened',
                'chest': chest
            }
        
        # Mark as opened
        chest['is_opened'] = True
        chest['opened_at'] = datetime.now().isoformat()
        
        # Parse reward data
        reward_data = json.loads(chest.get('reward_data', '{}'))
        
        return {
            'success': True,
            'message': f"🎉 {chest['chest_tier'].capitalize()} chest opened!",
            'chest': chest,
            'reward': reward_data,
            'tier': chest['chest_tier']
        }
    
    def get_chest_description(self, chest_tier: str) -> str:
        """
        Get user-friendly description of chest tier
        """
        descriptions = {
            'bronze': "🥉 Bronze Chest - Small reward from daily dedication",
            'silver': "🥈 Silver Chest - Nice reward for consistent progress",
            'gold': "🥇 Gold Chest - Great reward for major achievement",
            'platinum': "💎 Platinum Chest - Exceptional reward for milestone",
            'legendary': "👑 Legendary Chest - Ultimate reward for legendary achievement"
        }
        return descriptions.get(chest_tier, "Mystery Chest")


# Example usage and testing
if __name__ == "__main__":
    print("=== Reward Chest System Test ===\n")
    
    chest_system = RewardChestSystem()
    
    # Test chest tier determination
    print("Chest Tier Examples:")
    print(f"  Daily quest: {chest_system.determine_chest_tier('daily', 20)}")
    print(f"  Side quest: {chest_system.determine_chest_tier('side', 100)}")
    print(f"  Main quest: {chest_system.determine_chest_tier('main', 1500)}")
    print(f"  Level 25 milestone: {chest_system.determine_chest_tier('daily', 20, True, 25)}")
    print(f"  Level 100 milestone: {chest_system.determine_chest_tier('daily', 20, True, 100)}\n")
    
    # Generate sample chests
    print("Sample Reward Chests:")
    for tier in ['bronze', 'silver', 'gold']:
        if chest_system.should_drop_chest(tier):
            chest = chest_system.generate_reward_chest(tier, user_id=1, quest_id=123)
            print(f"\n{tier.capitalize()} Chest:")
            print(f"  Reward Type: {chest['reward_type']}")
            reward_data = json.loads(chest['reward_data'])
            print(f"  Description: {reward_data.get('description', 'N/A')}")
            if 'restaurant' in chest:
                print(f"  Restaurant: {chest['restaurant_name']}")
                print(f"  Value: ${chest['estimated_value']:.2f}")
    
    print("\n=== Test Complete ===")

