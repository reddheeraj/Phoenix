import logging
from typing import List, Dict, Any, Optional
from src.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class QuestAgentTools:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_quests(self, status: str = None, importance: str = None, urgency: str = None) -> List[Dict]:
        """Get quests with optional filters"""
        try:
            quests = self.db_manager.get_quests(status=status, importance=importance, urgency=urgency)
            return quests
        except Exception as e:
            logger.error(f"Failed to get quests: {e}")
            return []
    
    def get_quest_by_id(self, quest_id: int) -> Optional[Dict]:
        """Get specific quest by ID"""
        try:
            quests = self.db_manager.get_quests()
            for quest in quests:
                if quest['id'] == quest_id:
                    return quest
            return None
        except Exception as e:
            logger.error(f"Failed to get quest by ID: {e}")
            return None
    
    def update_quest_status(self, quest_id: int, status: str) -> bool:
        """Update quest status"""
        try:
            valid_statuses = ['pending', 'in_progress', 'completed', 'failed']
            if status not in valid_statuses:
                return False
            
            self.db_manager.update_quest_status(quest_id, status)
            return True
        except Exception as e:
            logger.error(f"Failed to update quest status: {e}")
            return False
    
    def get_quest_stats(self) -> Dict[str, Any]:
        """Get quest statistics"""
        try:
            stats = self.db_manager.get_quest_stats()
            return stats
        except Exception as e:
            logger.error(f"Failed to get quest stats: {e}")
            return {}
    
    def get_high_priority_quests(self) -> List[Dict]:
        """Get high priority quests (high urgency or main quests)"""
        try:
            high_urgency = self.db_manager.get_quests(urgency='high')
            critical_urgency = self.db_manager.get_quests(urgency='critical')
            main_quests = self.db_manager.get_quests(importance='main_quest')
            
            # Combine and deduplicate
            all_quests = high_urgency + critical_urgency + main_quests
            unique_quests = {quest['id']: quest for quest in all_quests}
            
            return list(unique_quests.values())
        except Exception as e:
            logger.error(f"Failed to get high priority quests: {e}")
            return []
    
    def get_pending_quests(self) -> List[Dict]:
        """Get all pending quests"""
        try:
            return self.db_manager.get_quests(status='pending')
        except Exception as e:
            logger.error(f"Failed to get pending quests: {e}")
            return []
    
    def get_completed_quests(self) -> List[Dict]:
        """Get all completed quests"""
        try:
            return self.db_manager.get_quests(status='completed')
        except Exception as e:
            logger.error(f"Failed to get completed quests: {e}")
            return []
    
    def get_quests_by_type(self, quest_type: str) -> List[Dict]:
        """Get quests by type"""
        try:
            quests = self.db_manager.get_quests()
            return [quest for quest in quests if quest['quest_type'] == quest_type]
        except Exception as e:
            logger.error(f"Failed to get quests by type: {e}")
            return []
    
    def get_quests_by_importance(self, importance: str) -> List[Dict]:
        """Get quests by importance level"""
        try:
            return self.db_manager.get_quests(importance=importance)
        except Exception as e:
            logger.error(f"Failed to get quests by importance: {e}")
            return []
    
    def get_quests_by_urgency(self, urgency: str) -> List[Dict]:
        """Get quests by urgency level"""
        try:
            return self.db_manager.get_quests(urgency=urgency)
        except Exception as e:
            logger.error(f"Failed to get quests by urgency: {e}")
            return []
    
    def get_quest_progress_summary(self) -> Dict[str, Any]:
        """Get quest progress summary"""
        try:
            stats = self.get_quest_stats()
            
            total_quests = sum(stats.get('status', {}).values())
            completed_quests = stats.get('status', {}).get('completed', 0)
            pending_quests = stats.get('status', {}).get('pending', 0)
            in_progress_quests = stats.get('status', {}).get('in_progress', 0)
            
            completion_rate = (completed_quests / total_quests * 100) if total_quests > 0 else 0
            
            return {
                'total_quests': total_quests,
                'completed_quests': completed_quests,
                'pending_quests': pending_quests,
                'in_progress_quests': in_progress_quests,
                'completion_rate': round(completion_rate, 2),
                'importance_breakdown': stats.get('importance', {}),
                'urgency_breakdown': stats.get('urgency', {})
            }
        except Exception as e:
            logger.error(f"Failed to get quest progress summary: {e}")
            return {}

