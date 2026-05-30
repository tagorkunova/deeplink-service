CREATE TABLE IF NOT EXISTS deeplinks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    target_url TEXT NOT NULL,
    payload JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    click_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS deeplink_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deeplink_id UUID REFERENCES deeplinks(id),
    event_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip VARCHAR(50),
    user_agent TEXT,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_deeplinks_code ON deeplinks(code);
CREATE INDEX IF NOT EXISTS idx_deeplinks_expires_at ON deeplinks(expires_at);
CREATE INDEX IF NOT EXISTS idx_deeplink_events_deeplink_id ON deeplink_events(deeplink_id);
