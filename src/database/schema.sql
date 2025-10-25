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

-- Quests table
CREATE TABLE IF NOT EXISTS quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    quest_type TEXT NOT NULL,
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

