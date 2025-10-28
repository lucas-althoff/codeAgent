--- Code Agent DB - Version 1

-- Enable UUID generation and extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS vector;

-- Analysis History Table
CREATE TABLE IF NOT EXISTS analysis_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_snippet VARCHAR(255) NOT NULL,
    suggestions TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);