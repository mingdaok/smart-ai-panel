-- database/schema.sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS rooms (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    expert_count INTEGER NOT NULL DEFAULT 4,
    status TEXT NOT NULL DEFAULT 'waiting'
        CHECK(status IN ('waiting','generating','ready','discussing','finished','stopped')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS experts (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    title TEXT NOT NULL,
    stance TEXT NOT NULL,
    color TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('host','expert')),
    position INTEGER NOT NULL DEFAULT 0,
    current_status TEXT NOT NULL DEFAULT 'idle'
        CHECK(current_status IN ('idle','preparing','speaking')),
    public_thought TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_experts_room ON experts(room_id);

CREATE TABLE IF NOT EXISTS transcript_lines (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    expert_id TEXT NOT NULL REFERENCES experts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    line_type TEXT NOT NULL CHECK(line_type IN ('opening','argument','rebuttal','supplement','question','closing')),
    sequence_num INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_transcript_room ON transcript_lines(room_id);
CREATE INDEX IF NOT EXISTS idx_transcript_seq ON transcript_lines(room_id, sequence_num);

CREATE TABLE IF NOT EXISTS insights (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK(type IN ('consensus','disagreement')),
    content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_insights_room ON insights(room_id);

CREATE TABLE IF NOT EXISTS discussion_events (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_events_room ON discussion_events(room_id);
