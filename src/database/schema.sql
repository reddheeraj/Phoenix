-- Emails table
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id TEXT UNIQUE NOT NULL,
    sender TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    received_date TIMESTAMP NOT NULL,
    processed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    daily_tasks TEXT NOT NULL, -- JSON array of daily tasks
    long_term_goals TEXT NOT NULL, -- JSON array of long-term goals
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User stats table for gamification
CREATE TABLE IF NOT EXISTS user_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    level INTEGER DEFAULT 0,
    total_xp INTEGER DEFAULT 0,
    current_xp INTEGER DEFAULT 0, -- XP in current level
    quests_completed INTEGER DEFAULT 0,
    daily_quests_completed INTEGER DEFAULT 0,
    email_quests_completed INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    last_activity_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quests table (updated to support different quest types)
CREATE TABLE IF NOT EXISTS quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    email_id INTEGER, -- NULL for daily tasks
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    quest_type TEXT NOT NULL, -- 'daily_task' or 'email_based'
    quest_category TEXT NOT NULL, -- 'daily', 'work', 'personal', etc.
    importance TEXT NOT NULL,
    urgency TEXT NOT NULL,
    deadline TIMESTAMP,
    event_duration_minutes INTEGER DEFAULT 60,
    calendar_event_id TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email_id) REFERENCES emails (id)
);

-- Email processing log table
CREATE TABLE IF NOT EXISTS email_processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_processed_datetime TIMESTAMP NOT NULL,
    emails_processed_count INTEGER DEFAULT 0,
    quests_created_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_emails_processed ON emails(processed);
CREATE INDEX IF NOT EXISTS idx_emails_received_date ON emails(received_date);
CREATE INDEX IF NOT EXISTS idx_quests_status ON quests(status);
CREATE INDEX IF NOT EXISTS idx_quests_importance ON quests(importance);
CREATE INDEX IF NOT EXISTS idx_quests_urgency ON quests(urgency);

