import sqlite3
import logging
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
                with open('src/database/schema.sql', 'r') as f:
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

