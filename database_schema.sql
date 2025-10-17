-- Natera Blog Crawler Database Schema
-- Run this in your SEPARATE Natera Supabase project

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- NEWS ARTICLES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS natera_news (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    author TEXT,
    published_date TIMESTAMP WITH TIME ZONE,
    featured_image TEXT,
    chunks JSONB,
    chunk_embeddings JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_natera_news_url ON natera_news(url);
CREATE INDEX IF NOT EXISTS idx_natera_news_published ON natera_news(published_date DESC);
CREATE INDEX IF NOT EXISTS idx_natera_news_chunks ON natera_news USING GIN (chunks);


-- ============================================================================
-- CANDIDATE PROFILES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS candidate_profiles (
    id SERIAL PRIMARY KEY,
    candidate_id TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    current_title TEXT,
    current_company TEXT,
    location TEXT,
    about_me TEXT,
    raw_profile JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_candidate_id ON candidate_profiles(candidate_id);
CREATE INDEX IF NOT EXISTS idx_candidate_name ON candidate_profiles(full_name);


-- ============================================================================
-- CANDIDATE EMBEDDINGS TABLE (Three-Field System)
-- ============================================================================

CREATE TABLE IF NOT EXISTS candidate_embeddings (
    id SERIAL PRIMARY KEY,
    candidate_profile_id INTEGER REFERENCES candidate_profiles(id) ON DELETE CASCADE,

    -- Three separate embedding fields
    professional_summary TEXT,
    professional_summary_embedding JSONB,

    job_preferences TEXT,
    job_preferences_embedding JSONB,

    interests TEXT,
    interests_embedding JSONB,

    -- Legacy fields for backwards compatibility
    embedding_text TEXT,
    embedding JSONB,

    token_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(candidate_profile_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_candidate_embeddings_profile ON candidate_embeddings(candidate_profile_id);


-- ============================================================================
-- JOB POSTINGS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS job_postings (
    id SERIAL PRIMARY KEY,
    job_id TEXT UNIQUE NOT NULL,
    position TEXT NOT NULL,
    company TEXT NOT NULL DEFAULT 'Natera',
    department TEXT,
    location_type TEXT,
    location_city TEXT,
    location_country TEXT,
    employment_type TEXT,
    compensation_currency TEXT,
    compensation_min NUMERIC,
    compensation_max NUMERIC,
    about_role TEXT,
    requirements JSONB,
    responsibilities JSONB,
    raw_job_data JSONB,
    application_link TEXT,
    posting_code TEXT,
    status TEXT DEFAULT 'active',
    posted_date TIMESTAMP WITH TIME ZONE,
    expires_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_job_postings_status ON job_postings(status);
CREATE INDEX IF NOT EXISTS idx_job_postings_location ON job_postings(location_city, location_country);
CREATE INDEX IF NOT EXISTS idx_job_postings_position ON job_postings(position);


-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to calculate cosine similarity between JSONB vectors
CREATE OR REPLACE FUNCTION cosine_similarity(vec1 JSONB, vec2 JSONB)
RETURNS FLOAT AS $$
DECLARE
    dot_product FLOAT := 0;
    magnitude1 FLOAT := 0;
    magnitude2 FLOAT := 0;
    i INTEGER;
    v1 FLOAT[];
    v2 FLOAT[];
BEGIN
    -- Convert JSONB to arrays
    SELECT ARRAY(SELECT jsonb_array_elements_text(vec1)::FLOAT) INTO v1;
    SELECT ARRAY(SELECT jsonb_array_elements_text(vec2)::FLOAT) INTO v2;

    -- Calculate dot product and magnitudes
    FOR i IN 1..array_length(v1, 1) LOOP
        dot_product := dot_product + (v1[i] * v2[i]);
        magnitude1 := magnitude1 + (v1[i] * v1[i]);
        magnitude2 := magnitude2 + (v2[i] * v2[i]);
    END LOOP;

    -- Return cosine similarity
    IF magnitude1 = 0 OR magnitude2 = 0 THEN
        RETURN 0;
    END IF;

    RETURN dot_product / (sqrt(magnitude1) * sqrt(magnitude2));
END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- ============================================================================
-- RPC FUNCTIONS FOR NEWS SEARCH
-- ============================================================================

-- Search news articles for a candidate using professional summary embedding
CREATE OR REPLACE FUNCTION search_news_for_candidate(
    p_candidate_id TEXT,
    p_match_threshold FLOAT DEFAULT 0.25,
    p_limit INTEGER DEFAULT 30
)
RETURNS TABLE (
    news_id INTEGER,
    news_title TEXT,
    news_url TEXT,
    news_author TEXT,
    news_featured_image TEXT,
    chunk_text TEXT,
    chunk_index INTEGER,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    WITH candidate_embedding AS (
        SELECT ce.professional_summary_embedding
        FROM candidate_embeddings ce
        JOIN candidate_profiles cp ON ce.candidate_profile_id = cp.id
        WHERE cp.candidate_id = p_candidate_id
        LIMIT 1
    ),
    chunk_similarities AS (
        SELECT
            n.id AS article_id,
            n.title AS article_title,
            n.url AS article_url,
            n.author AS article_author,
            n.featured_image AS article_image,
            chunk->>'text' AS text_content,
            (chunk->>'chunk_index')::INTEGER AS chunk_idx,
            cosine_similarity(
                ce.professional_summary_embedding,
                embedding->'embedding'
            ) AS sim_score
        FROM natera_news n
        CROSS JOIN candidate_embedding ce
        CROSS JOIN LATERAL jsonb_array_elements(n.chunks) AS chunk
        CROSS JOIN LATERAL jsonb_array_elements(n.chunk_embeddings) AS embedding
        WHERE (chunk->>'chunk_index')::INTEGER = (embedding->>'chunk_index')::INTEGER
    )
    SELECT
        cs.article_id,
        cs.article_title,
        cs.article_url,
        cs.article_author,
        cs.article_image,
        cs.text_content,
        cs.chunk_idx,
        cs.sim_score
    FROM chunk_similarities cs
    WHERE cs.sim_score >= p_match_threshold
    ORDER BY cs.sim_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- UPDATE TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_natera_news_updated_at BEFORE UPDATE ON natera_news
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_candidate_profiles_updated_at BEFORE UPDATE ON candidate_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_candidate_embeddings_updated_at BEFORE UPDATE ON candidate_embeddings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_postings_updated_at BEFORE UPDATE ON job_postings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
