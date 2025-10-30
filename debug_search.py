"""
Debug script to test news search functionality
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Initialize Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

print("=" * 80)
print("DEBUG: Natera News Search")
print("=" * 80)

# 1. Check how many news articles exist
print("\n1. Checking news articles in database...")
news_result = supabase.table('natera_news').select('id, title, url, published_date').execute()
print(f"   Total news articles: {len(news_result.data)}")
if news_result.data:
    print(f"   Sample article: {news_result.data[0]['title']}")
    print(f"   Published: {news_result.data[0].get('published_date', 'N/A')}")

# 2. Check if articles have chunks and embeddings
print("\n2. Checking article chunks and embeddings...")
if news_result.data:
    first_article = supabase.table('natera_news').select('chunks, chunk_embeddings').eq('id', news_result.data[0]['id']).execute()
    if first_article.data:
        article = first_article.data[0]
        chunks = article.get('chunks', [])
        embeddings = article.get('chunk_embeddings', [])
        print(f"   First article has {len(chunks) if chunks else 0} chunks")
        print(f"   First article has {len(embeddings) if embeddings else 0} embeddings")

        if chunks and isinstance(chunks, list) and len(chunks) > 0:
            print(f"   Sample chunk text: {chunks[0].get('text', '')[:100]}...")

        if embeddings and isinstance(embeddings, list) and len(embeddings) > 0:
            print(f"   Sample embedding has {len(embeddings[0].get('embedding', []))} dimensions")

# 3. Check candidate embeddings
print("\n3. Checking candidate embeddings...")
candidate_id = "pub_5d984f6178b4d04f6244fa78"
profile_result = supabase.table('candidate_profiles').select('id, full_name').eq('candidate_id', candidate_id).execute()
if profile_result.data:
    profile_id = profile_result.data[0]['id']
    print(f"   Found candidate: {profile_result.data[0]['full_name']} (profile_id: {profile_id})")

    # Check embeddings
    embedding_result = supabase.table('candidate_embeddings').select('professional_summary, professional_summary_embedding').eq('candidate_profile_id', profile_id).execute()
    if embedding_result.data:
        emb_data = embedding_result.data[0]
        summary = emb_data.get('professional_summary', '')
        embedding = emb_data.get('professional_summary_embedding', [])
        print(f"   Professional summary: {summary[:100]}...")
        print(f"   Embedding exists: {embedding is not None}")
        if embedding:
            print(f"   Embedding length: {len(embedding) if isinstance(embedding, list) else 'stored as JSONB'}")
else:
    print(f"   ERROR: Candidate {candidate_id} not found!")

# 4. Test the RPC function directly with very low threshold
print("\n4. Testing RPC function with threshold 0.1...")
try:
    result = supabase.rpc(
        'search_news_for_candidate_fast',
        {
            'p_candidate_id': candidate_id,
            'p_match_threshold': 0.1,
            'p_limit': 10
        }
    ).execute()

    print(f"   RPC returned {len(result.data)} results")
    if result.data:
        for i, match in enumerate(result.data[:3], 1):
            print(f"   {i}. {match.get('news_title', 'N/A')} (similarity: {match.get('similarity', 0):.3f})")
    else:
        print("   No matches found even with 0.1 threshold!")
except Exception as e:
    print(f"   ERROR calling RPC: {str(e)}")

# 5. Test with threshold 0.0 (return everything)
print("\n5. Testing RPC function with threshold 0.0 (show all)...")
try:
    result = supabase.rpc(
        'search_news_for_candidate_fast',
        {
            'p_candidate_id': candidate_id,
            'p_match_threshold': 0.0,
            'p_limit': 5
        }
    ).execute()

    print(f"   RPC returned {len(result.data)} results")
    if result.data:
        print("   Top 5 matches (any similarity):")
        for i, match in enumerate(result.data, 1):
            print(f"   {i}. Similarity: {match.get('similarity', 0):.4f} - {match.get('news_title', 'N/A')[:60]}")
    else:
        print("   ERROR: No results even with 0.0 threshold - something is wrong!")
except Exception as e:
    print(f"   ERROR calling RPC: {str(e)}")

print("\n" + "=" * 80)
print("Debug complete!")
print("=" * 80)
