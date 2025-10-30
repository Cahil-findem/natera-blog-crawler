"""
Natera News Crawler
Scrapes news articles from natera.com/company/news/ and stores them with embeddings
"""

import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI
import tiktoken
import xml.etree.ElementTree as ET

# Load environment variables
load_dotenv()

# Initialize clients
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configuration
BASE_URL = "https://www.natera.com/company/news/"
CHUNK_SIZE = 500  # tokens per chunk
CHUNK_OVERLAP = 50  # token overlap between chunks


def get_news_page_html(url):
    """Fetch HTML content from Natera news page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None


def extract_article_links_from_sitemap(limit=None):
    """Extract article links from Natera sitemap"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    # News sitemaps
    news_sitemaps = [
        'https://www.natera.com/nat-news-sitemap.xml',
        'https://www.natera.com/nat-pr-news-sitemap.xml'
    ]

    all_articles = []

    for sitemap_url in news_sitemaps:
        try:
            print(f"  Fetching sitemap: {sitemap_url}")
            response = requests.get(sitemap_url, headers=headers, timeout=30)

            if response.status_code == 200:
                root = ET.fromstring(response.content)
                namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

                urls = root.findall('.//ns:url/ns:loc', namespace)
                print(f"  Found {len(urls)} articles in sitemap")

                for url in urls:
                    all_articles.append(url.text)

        except Exception as e:
            print(f"  Error fetching sitemap: {str(e)}")

    # Apply limit if specified
    if limit:
        all_articles = all_articles[:limit]

    print(f"Total: {len(all_articles)} article links")
    return all_articles


def scrape_article(url):
    """Scrape a single news article"""
    html = get_news_page_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'lxml')

    # Extract title
    title = None
    title_selectors = [
        'h1.entry-title',
        'h1.post-title',
        'article h1',
        'h1',
    ]
    for selector in title_selectors:
        title_elem = soup.select_one(selector)
        if title_elem:
            title = title_elem.get_text(strip=True)
            break

    # Extract date
    published_date = None
    date_selectors = [
        'time',
        '.post-meta time',
        '.entry-date',
        'span.published',
    ]
    for selector in date_selectors:
        date_elem = soup.select_one(selector)
        if date_elem:
            date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
            try:
                published_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                pass
            break

    # Extract author
    author = "Natera"  # Default
    author_selectors = [
        '.author-name',
        '.post-author',
        'span.author',
    ]
    for selector in author_selectors:
        author_elem = soup.select_one(selector)
        if author_elem:
            author = author_elem.get_text(strip=True)
            break

    # Extract featured image
    featured_image = None
    img_selectors = [
        '.et_featured_image img',
        'article img',
        '.post-thumbnail img',
    ]
    for selector in img_selectors:
        img_elem = soup.select_one(selector)
        if img_elem:
            featured_image = img_elem.get('src')
            break

    # Extract main content
    content = ""
    content_selectors = [
        '.entry-content',
        'article .content',
        '.post-content',
        'article',
    ]
    for selector in content_selectors:
        content_elem = soup.select_one(selector)
        if content_elem:
            # Remove scripts, styles, and navigation
            for tag in content_elem.find_all(['script', 'style', 'nav', 'aside']):
                tag.decompose()
            content = content_elem.get_text(separator='\n', strip=True)
            break

    if not title or not content:
        print(f"Could not extract title or content from {url}")
        return None

    return {
        'title': title,
        'url': url,
        'content': content,
        'author': author,
        'published_date': published_date,
        'featured_image': featured_image,
    }


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks based on token count"""
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(text)

    chunks = []
    start = 0

    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)

        chunks.append({
            'text': chunk_text,
            'start_token': start,
            'end_token': end,
            'token_count': len(chunk_tokens)
        })

        start = end - overlap

    return chunks


def generate_embedding(text):
    """Generate embedding for text using OpenAI"""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def store_article(article):
    """Store article with embeddings in Supabase"""
    # Check if article already exists
    existing = supabase.table('natera_news').select('id').eq('url', article['url']).execute()

    if existing.data:
        print(f"Article already exists: {article['title']}")
        return existing.data[0]['id']

    # Chunk the content
    chunks = chunk_text(article['content'])
    print(f"Created {len(chunks)} chunks for: {article['title']}")

    # Generate embeddings for each chunk
    chunks_with_embeddings = []
    chunk_embeddings = []

    for i, chunk in enumerate(chunks):
        print(f"  Generating embedding for chunk {i+1}/{len(chunks)}...")
        embedding = generate_embedding(chunk['text'])

        # Store chunk data
        chunks_with_embeddings.append({
            'text': chunk['text'],
            'chunk_index': i,
            'token_count': chunk['token_count']
        })

        # Store embedding separately
        chunk_embeddings.append({
            'embedding': embedding,
            'chunk_index': i
        })

        time.sleep(0.1)  # Rate limiting

    # Store article with chunks and embeddings as JSONB
    article_data = {
        'title': article['title'],
        'url': article['url'],
        'content': article['content'],
        'author': article['author'],
        'published_date': article['published_date'].isoformat() if article['published_date'] else None,
        'featured_image': article['featured_image'],
        'chunks': chunks_with_embeddings,
        'chunk_embeddings': chunk_embeddings
    }

    result = supabase.table('natera_news').insert(article_data).execute()
    news_id = result.data[0]['id']

    print(f"✅ Stored article with {len(chunks)} chunks: {article['title']}")
    return news_id


def main(limit=10):
    """Main crawler function"""
    print("=" * 60)
    print("Natera News Crawler")
    print("=" * 60)
    print()

    # Extract article links from sitemap
    print("Fetching article links from sitemap...")
    article_links = extract_article_links_from_sitemap(limit=limit)

    if not article_links:
        print("❌ No articles found")
        return

    print(f"\n✅ Found {len(article_links)} articles to process")
    print("\nStarting article scraping...\n")

    # Scrape and store each article
    success_count = 0
    for i, url in enumerate(article_links, 1):
        print(f"[{i}/{len(article_links)}] Scraping: {url}")

        article = scrape_article(url)
        if article:
            try:
                store_article(article)
                success_count += 1
            except Exception as e:
                print(f"❌ Error storing article: {str(e)}")

        time.sleep(1)  # Be nice to the server

    print()
    print("=" * 60)
    print(f"✅ Crawling complete!")
    print(f"Successfully processed {success_count}/{len(article_links)} articles")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    # Allow passing limit as command line argument, default to 50
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    main(limit=limit)
