-- Priority Articles Table
-- Allows manual assignment of specific articles to specific candidates
-- These articles will ALWAYS appear in candidate emails regardless of semantic matching

CREATE TABLE IF NOT EXISTS candidate_priority_articles (
    id SERIAL PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    news_id INTEGER NOT NULL REFERENCES natera_news(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 1, -- Lower number = higher priority
    notes TEXT, -- Optional note about why this article was prioritized
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure a candidate doesn't have the same article prioritized twice
    UNIQUE(candidate_id, news_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_priority_articles_candidate ON candidate_priority_articles(candidate_id);
CREATE INDEX IF NOT EXISTS idx_priority_articles_news ON candidate_priority_articles(news_id);
CREATE INDEX IF NOT EXISTS idx_priority_articles_priority ON candidate_priority_articles(priority);

-- Trigger to update updated_at
CREATE TRIGGER update_candidate_priority_articles_updated_at
    BEFORE UPDATE ON candidate_priority_articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE candidate_priority_articles IS 'Manually assigned priority articles that will always appear in candidate emails';
COMMENT ON COLUMN candidate_priority_articles.candidate_id IS 'Reference to candidate_profiles.candidate_id';
COMMENT ON COLUMN candidate_priority_articles.news_id IS 'Reference to natera_news.id';
COMMENT ON COLUMN candidate_priority_articles.priority IS 'Lower number = higher priority (1 is highest)';
