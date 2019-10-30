CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    token TEXT
) WITHOUT ROWID;

CREATE INDEX idx_token
ON users (token);