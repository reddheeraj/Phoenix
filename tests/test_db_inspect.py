#!/usr/bin/env python3
"""
Test script to inspect database tables and print their contents.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.config.settings import settings

def print_table(cursor, table_name):
    """Print contents of a table"""
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name}")
    print('='*80)
    
    # Get table info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print("\nSchema:")
    for col in columns:
        col_id, col_name, col_type, not_null, default_val, pk = col
        pk_str = " PRIMARY KEY" if pk else ""
        not_null_str = " NOT NULL" if not_null else ""
        default_str = f" DEFAULT {default_val}" if default_val else ""
        print(f"  {col_name}: {col_type}{pk_str}{not_null_str}{default_str}")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\nTotal Rows: {count}")
    
    if count > 0:
        # Get all data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        
        print(f"\nData (showing first 10 rows):")
        print("-" * 80)
        
        # Print column headers
        header = " | ".join([f"{name:20}" for name in column_names])
        print(header)
        print("-" * 80)
        
        # Print rows (limit to 10)
        for row in rows[:10]:
            # Convert each value to string and handle encoding issues
            safe_values = []
            for val in row:
                try:
                    val_str = str(val)[:20].encode('ascii', 'replace').decode('ascii')
                    safe_values.append(f"{val_str:20}")
                except:
                    safe_values.append(f"{'<encoding error>':20}")
            row_str = " | ".join(safe_values)
            print(row_str)
    else:
        print("\n(No data in table)")

def inspect_database():
    """Inspect all tables in the database"""
    db_path = settings.DB_PATH
    
    print(f"\n[DATABASE INSPECTION] Inspecting Database: {db_path}")
    print(f"Timestamp: {datetime.now()}")
    
    if not os.path.exists(db_path):
        print(f"\n[ERROR] Database file not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\nFound {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")
        
        # Print each table
        for table in tables:
            print_table(cursor, table)
        
        # Print some useful queries
        print(f"\n{'='*80}")
        print("USEFUL QUERIES")
        print('='*80)
        
        # Quest stats by status
        print("\nQuest Stats by Status:")
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM quests 
            GROUP BY status
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # Quest stats by importance
        print("\nQuest Stats by Importance:")
        cursor.execute("""
            SELECT importance, COUNT(*) as count 
            FROM quests 
            GROUP BY importance
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # Quest stats by type
        print("\nQuest Stats by Type:")
        cursor.execute("""
            SELECT quest_type, COUNT(*) as count 
            FROM quests 
            GROUP BY quest_type
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # User stats summary
        print("\nUser Stats Summary:")
        cursor.execute("SELECT * FROM user_stats")
        rows = cursor.fetchall()
        if rows:
            column_names = [description[0] for description in cursor.description]
            for row in rows:
                print(f"\n  User: {row[0]}")
                for i, col_name in enumerate(column_names):
                    if i > 0:  # Skip user_id
                        print(f"    {col_name}: {row[i]}")
        else:
            print("  (No user stats found)")
        
        conn.close()
        
        print(f"\n{'='*80}")
        print("[SUCCESS] Database inspection complete!")
        print('='*80)
        
    except Exception as e:
        print(f"\n[ERROR] Error inspecting database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_database()

