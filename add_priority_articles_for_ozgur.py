#!/usr/bin/env python3
"""
Add priority articles for Ozgur Acar
"""
import json
from supabase import create_client

supabase = create_client(
    'https://ecmftyvlghhwodmpboib.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVjbWZ0eXZsZ2hod29kbXBib2liIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2MjA4ODgsImV4cCI6MjA3NjE5Njg4OH0.mcfNkHHgVkdROe4J_Q7K5yd4kdV8TSn0txK90maPrps'
)

OZGUR_ID = 'pub_5d984f6178b4d04f6244fa78'

# Missing articles to add
new_articles = [
    {
        'title': 'Natera Technology Featured in 300 Peer-Reviewed Publications, Underscoring Scientific Leadership in Precision Medicine',
        'url': 'https://www.natera.com/company/news/natera-technology-featured-in-300-peer-reviewed-publications-underscoring-scientific-leadership-in-precision-medicine/',
        'content': 'Natera has achieved a significant milestone with its technology featured in over 300 peer-reviewed publications, demonstrating the company\'s scientific leadership and commitment to advancing precision medicine through evidence-based research and clinical validation.',
        'author': 'Natera',
        'published_date': '2025-01-15',
        'featured_image': 'https://natera-blog-crawler.vercel.app/images/Natera-social.webp'
    },
    {
        'title': 'Natera Announces Medicare Coverage for Signatera Genome',
        'url': 'https://www.natera.com/company/news/natera-announces-medicare-coverage-for-signatera-genome/',
        'content': 'Natera announces expanded Medicare coverage for Signatera Genome, its personalized circulating tumor DNA (ctDNA) test, representing a major advancement in access to precision oncology monitoring for Medicare beneficiaries.',
        'author': 'Natera',
        'published_date': '2024-12-01',
        'featured_image': 'https://natera-blog-crawler.vercel.app/images/Natera-social.webp'
    }
]

print("Adding missing articles to database...\n")

article_ids = []

for article in new_articles:
    print(f"Processing: {article['title']}")

    # Check if exists
    existing = supabase.table('natera_news').select('id').eq('url', article['url']).execute()

    if existing.data:
        article_id = existing.data[0]['id']
        print(f"  ✓ Article already exists (ID: {article_id})")
        article_ids.append(article_id)
    else:
        # Add the article
        chunk_text = f"{article['title']}. {article['content']}"

        news_data = {
            'title': article['title'],
            'url': article['url'],
            'content': article['content'],
            'author': article['author'],
            'published_date': article['published_date'],
            'featured_image': article['featured_image'],
            'chunks': json.dumps([{
                'chunk_index': 0,
                'text': chunk_text,
                'token_count': len(chunk_text.split())
            }]),
            'chunk_embeddings': json.dumps([])
        }

        try:
            result = supabase.table('natera_news').insert(news_data).execute()
            article_id = result.data[0]['id']
            print(f"  ✓ Article added (ID: {article_id})")
            article_ids.append(article_id)
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            article_ids.append(None)
    print()

# Now we have article ID 1056 (Fast Company) + the 2 new ones
# Add priority articles for Ozgur
print("="*60)
print("Adding priority articles for Ozgur Acar...")
print("="*60)

# Get the Fast Company article ID
fast_company = supabase.table('natera_news').select('id').eq('url',
    'https://www.natera.com/company/news/natera-named-to-fast-companys-next-big-things-in-tech-list/'
).execute()

all_article_ids = [fast_company.data[0]['id']] + [aid for aid in article_ids if aid]

priority_data = []
for idx, article_id in enumerate(all_article_ids, 1):
    priority_data.append({
        'candidate_id': OZGUR_ID,
        'news_id': article_id,
        'priority': idx,
        'notes': f'Priority article {idx} for Ozgur'
    })

for item in priority_data:
    try:
        result = supabase.table('candidate_priority_articles').insert(item).execute()
        print(f"✓ Added news_id {item['news_id']} (priority {item['priority']})")
    except Exception as e:
        if 'duplicate key' in str(e).lower():
            print(f"✓ news_id {item['news_id']} already prioritized")
        else:
            print(f"✗ Error adding news_id {item['news_id']}: {str(e)}")

print("\n" + "="*60)
print("✅ Priority articles configured for Ozgur!")
print("="*60)
print(f"\nOzgur (ID: {OZGUR_ID}) now has {len(all_article_ids)} priority articles")
