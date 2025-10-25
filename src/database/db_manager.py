import sqlite3
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from src.config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DB_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
                conn.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def add_email(self, email_id: str, sender: str, subject: str, body: str, received_date: datetime) -> int:
        """Add email to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if email already exists
                cursor.execute("SELECT id, processed FROM emails WHERE email_id = ?", (email_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Email already exists, return existing ID
                    logger.info(f"Email {email_id} already exists with processed={existing[1]}")
                    return existing[0]
                
                # Insert new email
                cursor.execute("""
                    INSERT INTO emails (email_id, sender, subject, body, received_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (email_id, sender, subject, body, received_date))
                conn.commit()
                new_id = cursor.lastrowid
                logger.info(f"Added new email {email_id} with ID {new_id}")
                return new_id
        except Exception as e:
            logger.error(f"Failed to add email: {e}")
            raise
    
    def get_unprocessed_emails(self) -> List[Dict]:
        """Get all unprocessed emails"""
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM emails WHERE processed = 0 ORDER BY received_date")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get unprocessed emails: {e}")
            raise
    
    def mark_email_processed(self, email_id: int):
        """Mark email as processed"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE emails SET processed = 1 WHERE id = ?", (email_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to mark email as processed: {e}")
            raise
    
    def add_quest(self, email_id: int, title: str, description: str, quest_type: str, 
                  importance: str, urgency: str, deadline: datetime = None, 
                  event_duration_minutes: int = 60, calendar_event_id: str = None) -> int:
        """Add quest to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO quests (email_id, title, description, quest_type, importance, 
                                     urgency, deadline, event_duration_minutes, calendar_event_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (email_id, title, description, quest_type, importance, urgency, 
                      deadline, event_duration_minutes, calendar_event_id))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add quest: {e}")
            raise
    
    def get_quests(self, status: str = None, importance: str = None, urgency: str = None) -> List[Dict]:
        """Get quests with optional filters"""
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT q.*, e.sender, e.subject FROM quests q JOIN emails e ON q.email_id = e.id"
                conditions = []
                params = []
                
                if status:
                    conditions.append("q.status = ?")
                    params.append(status)
                if importance:
                    conditions.append("q.importance = ?")
                    params.append(importance)
                if urgency:
                    conditions.append("q.urgency = ?")
                    params.append(urgency)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY q.created_at DESC"
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get quests: {e}")
            raise
    
    def update_quest_status(self, quest_id: int, status: str):
        """Update quest status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE quests SET status = ? WHERE id = ?", (status, quest_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update quest status: {e}")
            raise
    
    def update_quest_calendar_event_id(self, quest_id: int, calendar_event_id: str):
        """Update quest calendar event ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE quests SET calendar_event_id = ? WHERE id = ?", 
                             (calendar_event_id, quest_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update quest calendar event ID: {e}")
            raise
    
    def get_last_processing_datetime(self) -> Optional[datetime]:
        """Get last processing datetime"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT last_processed_datetime FROM email_processing_log 
                    ORDER BY created_at DESC LIMIT 1
                """)
                result = cursor.fetchone()
                return datetime.fromisoformat(result[0]) if result and result[0] else None
        except Exception as e:
            logger.error(f"Failed to get last processing datetime: {e}")
            return None
    
    def log_processing(self, last_processed_datetime: datetime, emails_processed: int, quests_created: int):
        """Log processing statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO email_processing_log (last_processed_datetime, emails_processed_count, quests_created_count)
                    VALUES (?, ?, ?)
                """, (last_processed_datetime, emails_processed, quests_created))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log processing: {e}")
            raise
    
    def get_quest_stats(self) -> Dict:
        """Get quest statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total quests by status
                cursor.execute("""
                    SELECT status, COUNT(*) as count FROM quests GROUP BY status
                """)
                status_stats = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Total quests by importance
                cursor.execute("""
                    SELECT importance, COUNT(*) as count FROM quests GROUP BY importance
                """)
                importance_stats = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Total quests by urgency
                cursor.execute("""
                    SELECT urgency, COUNT(*) as count FROM quests GROUP BY urgency
                """)
                urgency_stats = {row[0]: row[1] for row in cursor.fetchall()}
                
                return {
                    "status": status_stats,
                    "importance": importance_stats,
                    "urgency": urgency_stats
                }
        except Exception as e:
            logger.error(f"Failed to get quest stats: {e}")
            return {}
    
    # User Preferences Methods
    def create_user_preferences(self, user_id: str, daily_tasks: List[str], long_term_goals: List[str]) -> int:
        """Create user preferences"""
        try:
            import json
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_preferences (user_id, daily_tasks, long_term_goals, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (user_id, json.dumps(daily_tasks), json.dumps(long_term_goals), datetime.now()))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to create user preferences: {e}")
            raise
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        """Get user preferences"""
        try:
            import json
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT daily_tasks, long_term_goals FROM user_preferences WHERE user_id = ?", (user_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        'daily_tasks': json.loads(result[0]),
                        'long_term_goals': json.loads(result[1])
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            raise
    
    def update_user_preferences(self, user_id: str, daily_tasks: List[str] = None, long_term_goals: List[str] = None) -> bool:
        """Update user preferences"""
        try:
            import json
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get current preferences
                current = self.get_user_preferences(user_id)
                if not current:
                    return False
                
                # Update only provided fields
                updated_daily_tasks = daily_tasks if daily_tasks is not None else current['daily_tasks']
                updated_long_term_goals = long_term_goals if long_term_goals is not None else current['long_term_goals']
                
                cursor.execute("""
                    UPDATE user_preferences 
                    SET daily_tasks = ?, long_term_goals = ?, updated_at = ?
                    WHERE user_id = ?
                """, (json.dumps(updated_daily_tasks), json.dumps(updated_long_term_goals), datetime.now(), user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to update user preferences: {e}")
            raise
    
    # Updated Quest Methods
    def add_quest(self, user_id: str, email_id: Optional[int], title: str, description: str, 
                  quest_type: str, quest_category: str, importance: str, urgency: str, 
                  deadline: Optional[datetime] = None, event_duration_minutes: int = 60) -> int:
        """Add quest to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO quests (user_id, email_id, title, description, quest_type, quest_category, 
                                     importance, urgency, deadline, event_duration_minutes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, email_id, title, description, quest_type, quest_category, 
                      importance, urgency, deadline, event_duration_minutes))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add quest: {e}")
            raise
    
    def get_user_quests(self, user_id: str, quest_type: str = None) -> List[Dict]:
        """Get user quests, optionally filtered by type"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if quest_type:
                    cursor.execute("""
                        SELECT id, email_id, title, description, quest_type, quest_category, 
                               importance, urgency, deadline, event_duration_minutes, 
                               calendar_event_id, status, created_at
                        FROM quests WHERE user_id = ? AND quest_type = ?
                        ORDER BY created_at DESC
                    """, (user_id, quest_type))
                else:
                    cursor.execute("""
                        SELECT id, email_id, title, description, quest_type, quest_category, 
                               importance, urgency, deadline, event_duration_minutes, 
                               calendar_event_id, status, created_at
                        FROM quests WHERE user_id = ?
                        ORDER BY created_at DESC
                    """, (user_id,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get user quests: {e}")
            raise
    
    # Gamification Methods
    def create_user_stats(self, user_id: str) -> int:
        """Create user stats for gamification"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO user_stats (user_id, level, total_xp, current_xp, 
                                                     quests_completed, daily_quests_completed, 
                                                     email_quests_completed, streak_days, last_activity_date)
                    VALUES (?, 0, 0, 0, 0, 0, 0, 0, ?)
                """, (user_id, datetime.now().date()))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to create user stats: {e}")
            raise
    
    def get_user_stats(self, user_id: str) -> Optional[Dict]:
        """Get user stats"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT level, total_xp, current_xp, quests_completed, daily_quests_completed, 
                           email_quests_completed, streak_days, last_activity_date
                    FROM user_stats WHERE user_id = ?
                """, (user_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        'user_id': user_id,
                        'level': result[0],
                        'total_xp': result[1],
                        'current_xp': result[2],
                        'quests_completed': result[3],
                        'daily_quests_completed': result[4],
                        'email_quests_completed': result[5],
                        'streak_days': result[6],
                        'last_activity_date': result[7]
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            raise
    
    def calculate_xp_reward(self, quest_type: str, importance: str, urgency: str) -> int:
        """Calculate XP reward based on quest characteristics"""
        base_xp = {
            'daily_task': 10,
            'email_based': 25
        }
        
        importance_multiplier = {
            'daily': 1.0,
            'weekly': 1.2,
            'main_quest': 1.5,
            'side_quest': 0.8
        }
        
        urgency_multiplier = {
            'low': 0.8,
            'medium': 1.0,
            'high': 1.3,
            'critical': 1.5
        }
        
        base = base_xp.get(quest_type, 20)
        importance_mult = importance_multiplier.get(importance, 1.0)
        urgency_mult = urgency_multiplier.get(urgency, 1.0)
        
        return int(base * importance_mult * urgency_mult)
    
    def calculate_level_xp_required(self, level: int) -> int:
        """Calculate XP required for a specific level"""
        # More reasonable growth: Level 1 = 50 XP, Level 2 = 100 XP, Level 3 = 150 XP, etc.
        return int(50 * level)
    
    def complete_quest(self, quest_id: int, user_id: str) -> Dict:
        """Complete a quest and award XP"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get quest details
                cursor.execute("""
                    SELECT quest_type, importance, urgency, status FROM quests 
                    WHERE id = ? AND user_id = ?
                """, (quest_id, user_id))
                quest = cursor.fetchone()
                
                if not quest:
                    raise ValueError("Quest not found or doesn't belong to user")
                
                if quest[3] == 'completed':
                    raise ValueError("Quest already completed")
                
                quest_type, importance, urgency, status = quest
                
                # Calculate XP reward
                xp_reward = self.calculate_xp_reward(quest_type, importance, urgency)
                
                # Get current user stats
                stats = self.get_user_stats(user_id)
                if not stats:
                    # Create stats if they don't exist
                    self.create_user_stats(user_id)
                    stats = self.get_user_stats(user_id)
                
                # Update XP and level
                new_total_xp = stats['total_xp'] + xp_reward
                new_current_xp = stats['current_xp'] + xp_reward
                new_level = stats['level']
                
                # Check for level up
                xp_for_next_level = self.calculate_level_xp_required(new_level + 1)
                level_ups = 0
                
                while new_current_xp >= xp_for_next_level:
                    new_level += 1
                    level_ups += 1
                    new_current_xp -= xp_for_next_level
                    xp_for_next_level = self.calculate_level_xp_required(new_level + 1)
                
                # Update quest status
                cursor.execute("""
                    UPDATE quests SET status = 'completed' WHERE id = ?
                """, (quest_id,))
                
                # Update user stats
                today = datetime.now().date()
                last_activity = stats['last_activity_date']
                
                # Calculate streak
                new_streak = stats['streak_days']
                if last_activity:
                    days_diff = (today - datetime.strptime(last_activity, '%Y-%m-%d').date()).days
                    if days_diff == 1:
                        new_streak += 1
                    elif days_diff > 1:
                        new_streak = 1
                else:
                    new_streak = 1
                
                # Update quest completion counters
                daily_completed = stats['daily_quests_completed']
                email_completed = stats['email_quests_completed']
                
                if quest_type == 'daily_task':
                    daily_completed += 1
                else:
                    email_completed += 1
                
                cursor.execute("""
                    UPDATE user_stats 
                    SET level = ?, total_xp = ?, current_xp = ?, quests_completed = quests_completed + 1,
                        daily_quests_completed = ?, email_quests_completed = ?, 
                        streak_days = ?, last_activity_date = ?, updated_at = ?
                    WHERE user_id = ?
                """, (new_level, new_total_xp, new_current_xp, daily_completed, email_completed, 
                      new_streak, today, datetime.now(), user_id))
                
                conn.commit()
                
                return {
                    'quest_id': quest_id,
                    'xp_reward': xp_reward,
                    'new_level': new_level,
                    'level_ups': level_ups,
                    'new_total_xp': new_total_xp,
                    'new_current_xp': new_current_xp,
                    'streak_days': new_streak
                }
                
        except Exception as e:
            logger.error(f"Failed to complete quest: {e}")
            raise
    
    def get_quests_without_calendar_events(self) -> List[Dict]:
        """Get all quests that don't have calendar events"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, user_id, title, description, quest_type, importance, 
                           urgency, deadline, event_duration_minutes
                    FROM quests 
                    WHERE calendar_event_id IS NULL AND deadline IS NOT NULL
                    ORDER BY created_at DESC
                """)
                results = cursor.fetchall()
                
                quests = []
                for row in results:
                    quests.append({
                        'id': row[0],
                        'user_id': row[1],
                        'title': row[2],
                        'description': row[3],
                        'quest_type': row[4],
                        'importance': row[5],
                        'urgency': row[6],
                        'deadline': row[7],
                        'event_duration_minutes': row[8]
                    })
                
                return quests
        except Exception as e:
            logger.error(f"Failed to get quests without calendar events: {e}")
            raise
    
    def get_user_quests_without_calendar_events(self, user_id: str) -> List[Dict]:
        """Get user's quests that don't have calendar events"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, user_id, title, description, quest_type, importance, 
                           urgency, deadline, event_duration_minutes
                    FROM quests 
                    WHERE user_id = ? AND calendar_event_id IS NULL AND deadline IS NOT NULL
                    ORDER BY created_at DESC
                """, (user_id,))
                results = cursor.fetchall()
                
                quests = []
                for row in results:
                    quests.append({
                        'id': row[0],
                        'user_id': row[1],
                        'title': row[2],
                        'description': row[3],
                        'quest_type': row[4],
                        'importance': row[5],
                        'urgency': row[6],
                        'deadline': row[7],
                        'event_duration_minutes': row[8]
                    })
                
                return quests
        except Exception as e:
            logger.error(f"Failed to get user quests without calendar events: {e}")
            raise

