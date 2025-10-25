#!/usr/bin/env python3
"""
Reset database script - deletes the old database and recreates with new schema.
USE WITH CAUTION: This will delete all existing data!
"""

import sys
import os
import sqlite3

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.config.settings import settings

def reset_database():
    """Delete and recreate the database with the latest schema"""
    db_path = settings.DB_PATH
    
    print(f"\n[RESET DATABASE] Target: {db_path}")
    
    # Check if database exists
    if os.path.exists(db_path):
        print(f"[WARNING] Database file exists and will be DELETED!")
        
        # Get confirmation
        response = input("Are you sure you want to delete the database? Type 'YES' to confirm: ")
        if response != 'YES':
            print("[CANCELLED] Database reset cancelled.")
            return
        
        # Delete the database
        try:
            os.remove(db_path)
            print(f"[SUCCESS] Deleted old database: {db_path}")
        except Exception as e:
            print(f"[ERROR] Failed to delete database: {e}")
            return
    else:
        print(f"[INFO] Database does not exist yet.")
    
    # Recreate the database with new schema
    try:
        from src.database.db_manager import DatabaseManager
        
        print(f"[INFO] Creating new database with latest schema...")
        db_manager = DatabaseManager(db_path)
        print(f"[SUCCESS] Database created successfully!")
        
        # Verify tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"\n[INFO] Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")
        
        print(f"\n[SUCCESS] Database reset complete!")
        print(f"[NEXT STEPS]")
        print(f"  1. Restart your API server if it's running")
        print(f"  2. Complete onboarding in the frontend")
        print(f"  3. Click 'Sync Emails' to process your Gmail")
        
    except Exception as e:
        print(f"[ERROR] Failed to create database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reset_database()

