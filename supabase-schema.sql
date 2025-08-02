-- Supabase SQL script to create tables
-- Run this in Supabase SQL Editor

-- Line Users table
CREATE TABLE IF NOT EXISTS line_users (
    id SERIAL PRIMARY KEY,
    line_id VARCHAR UNIQUE NOT NULL,
    name VARCHAR,
    picture VARCHAR,
    mode VARCHAR DEFAULT 'bot',
    added_at TIMESTAMP DEFAULT NOW(),
    blocked_at TIMESTAMP
);
CREATE INDEX idx_line_users_line_id ON line_users(line_id);

-- Chat Messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    line_user_id VARCHAR NOT NULL,
    message TEXT,
    is_from_user BOOLEAN,
    timestamp TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_chat_messages_user ON chat_messages(line_user_id);

-- Event Logs table
CREATE TABLE IF NOT EXISTS event_logs (
    id SERIAL PRIMARY KEY,
    line_user_id VARCHAR NOT NULL,
    event_type VARCHAR,
    timestamp TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_event_logs_user ON event_logs(line_user_id);

-- Message Categories table
CREATE TABLE IF NOT EXISTS message_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR DEFAULT '#3B82F6',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Message Templates table
CREATE TABLE IF NOT EXISTS message_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    message_type VARCHAR NOT NULL,
    category_id INTEGER REFERENCES message_categories(id),
    content JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    tags VARCHAR,
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_templates_category ON message_templates(category_id);
CREATE INDEX idx_templates_type ON message_templates(message_type);
CREATE INDEX idx_templates_name ON message_templates(name);

-- Template Usage Logs table
CREATE TABLE IF NOT EXISTS template_usage_logs (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES message_templates(id),
    line_user_id VARCHAR NOT NULL,
    context TEXT,
    success BOOLEAN DEFAULT TRUE,
    timestamp TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_usage_logs_template ON template_usage_logs(template_id);
CREATE INDEX idx_usage_logs_user ON template_usage_logs(line_user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE line_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE event_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE template_usage_logs ENABLE ROW LEVEL SECURITY;

-- Create policies for service role (full access)
CREATE POLICY "Service role full access" ON line_users FOR ALL USING (true);
CREATE POLICY "Service role full access" ON chat_messages FOR ALL USING (true);
CREATE POLICY "Service role full access" ON event_logs FOR ALL USING (true);
CREATE POLICY "Service role full access" ON message_categories FOR ALL USING (true);
CREATE POLICY "Service role full access" ON message_templates FOR ALL USING (true);
CREATE POLICY "Service role full access" ON template_usage_logs FOR ALL USING (true);

-- Insert default categories
INSERT INTO message_categories (name, description, color) VALUES
('General', 'ข้อความทั่วไป', '#3B82F6'),
('HR Policies', 'นโยบาย HR', '#10B981'),
('Leave', 'การลา', '#F59E0B'),
('Benefits', 'สวัสดิการ', '#8B5CF6'),
('Training', 'การฝึกอบรม', '#EC4899')
ON CONFLICT (name) DO NOTHING;
