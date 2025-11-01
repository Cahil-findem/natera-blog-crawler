#!/usr/bin/env python3
"""
Add priority/pinned articles for Carol-Ann that will always be included in her emails
"""
import os
import json
from datetime import datetime
from supabase import create_client

# Initialize Supabase
supabase = create_client(
    'https://ecmftyvlghhwodmpboib.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVjbWZ0eXZsZ2hod29kbXBib2liIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2MjA4ODgsImV4cCI6MjA3NjE5Njg4OH0.mcfNkHHgVkdROe4J_Q7K5yd4kdV8TSn0txK90maPrps'
)

# Carol-Ann's candidate ID
CAROL_ANN_ID = 'pub_cs_677938b45911ed1d97316bc9'

# Priority articles for Carol-Ann
priority_articles = [
    {
        'title': 'Natera to Report Third Quarter Results on November 6, 2025',
        'url': 'https://www.natera.com/company/news/natera-to-report-its-third-quarter-results-on-november-6-2025/',
        'content': 'Natera will release its third quarter 2025 financial results on November 6, 2025. This earnings announcement will provide insights into the company\'s recent performance and growth trajectory in genetic testing and precision medicine.',
        'author': 'Natera',
        'published_date': '2025-10-30',
        'featured_image': 'https://natera-blog-crawler.vercel.app/images/Natera-social.webp'
    },
    {
        'title': 'Natera Named to Fast Company\'s Next Big Things in Tech List',
        'url': 'https://www.natera.com/company/news/natera-named-to-fast-companys-next-big-things-in-tech-list/',
        'content': 'Natera has been recognized by Fast Company as one of the Next Big Things in Tech, highlighting the company\'s innovative approach to genetic testing and precision medicine. This recognition underscores Natera\'s position as a leader in healthcare technology and genomics.',
        'author': 'Natera',
        'published_date': '2025-10-16',
        'featured_image': 'https://natera-blog-crawler.vercel.app/images/Natera-social.webp'
    }
]

print(f"Adding priority articles for Carol-Ann ({CAROL_ANN_ID})...")
print(f"Number of articles to add: {len(priority_articles)}\n")

for article in priority_articles:
    print(f"Processing: {article['title']}")

    # Check if article already exists
    existing = supabase.table('natera_news').select('id').eq('url', article['url']).execute()

    if existing.data:
        print(f"  ✓ Article already exists (ID: {existing.data[0]['id']})")
    else:
        # Add the article to the database
        # Create a simple chunk for matching
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
            'chunk_embeddings': json.dumps([])  # We'll add embeddings if needed
        }

        try:
            result = supabase.table('natera_news').insert(news_data).execute()
            print(f"  ✓ Article added (ID: {result.data[0]['id']})")
        except Exception as e:
            print(f"  ✗ Error adding article: {str(e)}")

    print()

print("\n" + "="*60)
print("✅ Priority articles configured for Carol-Ann!")
print("="*60)
print("\nThese articles will now appear when matching news for Carol-Ann.")
print("To ensure they're prioritized, they've been added to the database.")
print("\nNext step: Generate an email for Carol-Ann to see these articles!")
