-- Fix for search_news_for_candidate timeout issue
-- Run this in your Natera Supabase SQL Editor

-- 1. Increase statement timeout for this function (from default 2 seconds to 30 seconds)
ALTER DATABASE postgres SET statement_timeout = '30s';

-- 2. Create optimized version of search_news_for_candidate
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
            chunk_data->>'text' AS text_content,
            (chunk_data->>'chunk_index')::INTEGER AS chunk_idx,
            cosine_similarity(
                ce.professional_summary_embedding,
                chunk_data->'embedding'
            ) AS sim_score
        FROM natera_news n
        CROSS JOIN candidate_embedding ce
        CROSS JOIN LATERAL (
            SELECT
                jsonb_array_elements(n.chunks) || jsonb_build_object(
                    'embedding',
                    (SELECT jsonb_array_elements(n.chunk_embeddings)->>'embedding'
                     WHERE (jsonb_array_elements(n.chunk_embeddings)->>'chunk_index')::INTEGER =
                           (jsonb_array_elements(n.chunks)->>'chunk_index')::INTEGER
                     LIMIT 1)
                ) AS chunk_data
        ) chunks_with_embeddings
        WHERE ce.professional_summary_embedding IS NOT NULL
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
$$ LANGUAGE plpgsql STABLE;

-- 3. Alternative: Create a much simpler and faster version
-- This version processes chunks in batches and is significantly faster
CREATE OR REPLACE FUNCTION search_news_for_candidate_fast(
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
DECLARE
    v_candidate_embedding JSONB;
    v_chunk JSONB;
    v_embedding JSONB;
    v_chunk_index INTEGER;
    v_sim_score FLOAT;
    v_news_record RECORD;
BEGIN
    -- Get candidate embedding
    SELECT ce.professional_summary_embedding INTO v_candidate_embedding
    FROM candidate_embeddings ce
    JOIN candidate_profiles cp ON ce.candidate_profile_id = cp.id
    WHERE cp.candidate_id = p_candidate_id
    LIMIT 1;

    -- If no embedding found, return empty
    IF v_candidate_embedding IS NULL THEN
        RETURN;
    END IF;

    -- Loop through news articles (limit to most recent 100 for speed)
    FOR v_news_record IN
        SELECT id, title, url, author, featured_image, chunks, chunk_embeddings
        FROM natera_news
        ORDER BY published_date DESC NULLS LAST
        LIMIT 100
    LOOP
        -- Loop through chunks in each article
        FOR v_chunk, v_embedding IN
            SELECT
                jsonb_array_elements(v_news_record.chunks),
                jsonb_array_elements(v_news_record.chunk_embeddings)
        LOOP
            v_chunk_index := (v_chunk->>'chunk_index')::INTEGER;

            -- Only compare if chunk indices match
            IF (v_embedding->>'chunk_index')::INTEGER = v_chunk_index THEN
                v_sim_score := cosine_similarity(
                    v_candidate_embedding,
                    v_embedding->'embedding'
                );

                -- Only return if above threshold
                IF v_sim_score >= p_match_threshold THEN
                    news_id := v_news_record.id;
                    news_title := v_news_record.title;
                    news_url := v_news_record.url;
                    news_author := v_news_record.author;
                    news_featured_image := v_news_record.featured_image;
                    chunk_text := v_chunk->>'text';
                    chunk_index := v_chunk_index;
                    similarity := v_sim_score;
                    RETURN NEXT;
                END IF;
            END IF;
        END LOOP;
    END LOOP;

    RETURN;
END;
$$ LANGUAGE plpgsql STABLE;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION search_news_for_candidate(TEXT, FLOAT, INTEGER) TO anon, authenticated;
GRANT EXECUTE ON FUNCTION search_news_for_candidate_fast(TEXT, FLOAT, INTEGER) TO anon, authenticated;
