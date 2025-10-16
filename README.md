# Natera Blog Crawler

AI-powered candidate nurture email system that matches candidates to relevant Natera news articles and job openings using semantic similarity and LLM evaluation.

## Architecture

**Completely separate from Kong Blog Crawler - no shared data or infrastructure**

### Components

1. **News Crawler** (`natera_news_crawler.py`)
   - Scrapes articles from https://www.natera.com/company/news/
   - Extracts content, metadata, images
   - Chunks and vectorizes content

2. **Candidate Vectorizer** (`vectorize_candidates.py`)
   - Creates 3-field embeddings (professional_summary, job_preferences, interests)
   - Stores in dedicated Natera Supabase database

3. **Matching Engine** (`match_candidates_to_news.py`)
   - Semantic similarity search for news articles
   - LLM-based job matching evaluation

4. **Flask API** (`app.py`)
   - `/api/process-candidate` - Vectorize and match
   - `/api/generate-email` - Generate personalized emails
   - `/api/update-context` - Update candidate context

## Database Schema

**Separate Supabase project for Natera**

### Tables
- `candidate_profiles` - Candidate information
- `candidate_embeddings` - Three-field embeddings
- `natera_news` - News articles with chunks and embeddings
- `job_postings` - Natera job openings

## Setup

1. Create separate Supabase project for Natera
2. Set environment variables:
   ```
   SUPABASE_URL=your_natera_supabase_url
   SUPABASE_KEY=your_natera_supabase_key
   OPENAI_API_KEY=your_openai_key
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run crawler:
   ```bash
   python natera_news_crawler.py
   ```

5. Start API:
   ```bash
   python app.py
   ```

## Deployment

Deploy to Vercel separately from Kong Blog Crawler:
- Different repository
- Different environment variables
- Different Vercel project

## Key Differences from Kong

- News articles instead of technical blogs
- Natera-specific job postings
- Separate candidate database
- Independent deployment
