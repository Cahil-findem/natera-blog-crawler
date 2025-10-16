"""
Match candidates to relevant Natera news articles using vector similarity
Adapted from Kong Blog Crawler's match_candidates_to_blogs.py
"""

import os
import json
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class CandidateNewsMatcher:
    """Match candidates to relevant Natera news articles using vector similarity"""

    def __init__(self):
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

        self.supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")

        # Initialize OpenAI client
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set in .env file")

        self.openai_client = OpenAI(api_key=openai_api_key)
        logger.info("OpenAI client initialized")

    def get_candidate_by_id(self, candidate_id: str) -> Optional[Dict]:
        """Fetch candidate profile and embedding by candidate ID"""
        try:
            # Get candidate profile
            profile_result = self.supabase.table('candidate_profiles')\
                .select('*')\
                .eq('candidate_id', candidate_id)\
                .execute()

            if not profile_result.data:
                logger.warning(f"No candidate found with ID: {candidate_id}")
                return None

            profile = profile_result.data[0]
            profile_id = profile['id']

            # Get candidate embeddings
            embedding_result = self.supabase.table('candidate_embeddings')\
                .select('*')\
                .eq('candidate_profile_id', profile_id)\
                .execute()

            if embedding_result.data:
                # Merge embeddings into profile
                profile.update(embedding_result.data[0])
                profile['profile_id'] = profile_id

            return profile

        except Exception as e:
            logger.error(f"Error fetching candidate: {str(e)}")
            return None

    def find_news_for_candidate(
        self,
        candidate_id: str,
        match_threshold: float = 0.25,
        match_count: int = 30,
        deduplicate: bool = True
    ) -> List[Dict]:
        """
        Find relevant news articles for a candidate

        Args:
            candidate_id: External candidate ID
            match_threshold: Minimum similarity score (0-1)
            match_count: Number of articles to return
            deduplicate: If True, return unique articles (best matching chunk per article)

        Returns:
            List of matching news articles with similarity scores
        """
        try:
            # Use the RPC function from database_schema.sql
            result = self.supabase.rpc(
                'search_news_for_candidate',
                {
                    'p_candidate_id': candidate_id,
                    'p_match_threshold': match_threshold,
                    'p_limit': match_count
                }
            ).execute()

            if not result.data:
                logger.info(f"No matching news found for candidate {candidate_id}")
                return []

            # Format results for consistency with Kong format
            formatted_results = []
            if deduplicate:
                # Group by news article and keep best matching chunk
                news_map = {}
                for row in result.data:
                    news_id = row['news_id']
                    if news_id not in news_map or row['similarity'] > news_map[news_id]['max_similarity']:
                        news_map[news_id] = {
                            'news_id': news_id,
                            'news_title': row['news_title'],
                            'news_url': row['news_url'],
                            'news_author': row['news_author'],
                            'news_featured_image': row['news_featured_image'],
                            'best_matching_chunk': row['chunk_text'],
                            'max_similarity': row['similarity']
                        }
                formatted_results = list(news_map.values())
            else:
                # Return all chunks
                formatted_results = [
                    {
                        'news_id': row['news_id'],
                        'news_title': row['news_title'],
                        'news_url': row['news_url'],
                        'news_author': row['news_author'],
                        'news_featured_image': row['news_featured_image'],
                        'chunk_text': row['chunk_text'],
                        'chunk_index': row['chunk_index'],
                        'similarity': row['similarity']
                    }
                    for row in result.data
                ]

            logger.info(f"Found {len(formatted_results)} matching news articles for candidate {candidate_id}")
            return formatted_results

        except Exception as e:
            logger.error(f"Error finding news for candidate: {str(e)}")
            return []

    def generate_email_recommendations(
        self,
        candidate_id: str,
        num_articles: int = 3,
        match_threshold: float = 0.25
    ) -> Dict:
        """
        Generate personalized news recommendations for email nurturing

        Args:
            candidate_id: External candidate ID
            num_articles: Number of articles to recommend
            match_threshold: Minimum similarity score

        Returns:
            Dict with candidate info and recommended articles
        """
        try:
            # Get candidate info
            candidate = self.get_candidate_by_id(candidate_id)
            if not candidate:
                return None

            # Find matching news
            news_articles = self.find_news_for_candidate(
                candidate_id,
                match_threshold=match_threshold,
                match_count=num_articles,
                deduplicate=True
            )

            # Format for email
            recommendations = {
                'candidate': {
                    'name': candidate.get('full_name', 'there'),
                    'email': candidate.get('email', ''),
                    'current_title': candidate.get('current_title', ''),
                },
                'recommended_articles': [
                    {
                        'title': article['news_title'],
                        'url': article['news_url'],
                        'author': article.get('news_author', 'Natera'),
                        'featured_image': article.get('news_featured_image', ''),
                        'relevance_score': round(article.get('max_similarity', 0) * 100, 1),
                        'excerpt': article.get('best_matching_chunk', '')[:200] + '...'
                    }
                    for article in news_articles
                ]
            }

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return None

    def print_recommendations(self, candidate_id: str, num_articles: int = 5):
        """
        Print formatted recommendations for a candidate (for testing/demo)

        Args:
            candidate_id: External candidate ID
            num_articles: Number of articles to show
        """
        recommendations = self.generate_email_recommendations(
            candidate_id,
            num_articles=num_articles
        )

        if not recommendations:
            print(f"No recommendations found for candidate {candidate_id}")
            return

        candidate = recommendations['candidate']
        articles = recommendations['recommended_articles']

        print(f"\n{'='*80}")
        print(f"PERSONALIZED NEWS RECOMMENDATIONS")
        print(f"{'='*80}")
        print(f"Candidate: {candidate['name']}")
        if candidate['current_title']:
            print(f"Role: {candidate['current_title']}")
        print(f"\nTop {len(articles)} Recommended Articles:")
        print(f"{'='*80}\n")

        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   Relevance: {article['relevance_score']}%")
            print(f"   URL: {article['url']}")
            if article['author']:
                print(f"   Author: {article['author']}")
            print(f"   Excerpt: {article['excerpt']}")
            print()

        print(f"{'='*80}\n")


def main():
    """Main entry point"""
    import sys

    matcher = CandidateNewsMatcher()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python match_candidates_to_news.py <candidate_id> [num_articles]")
        print("\nExample:")
        print("  python match_candidates_to_news.py pub_hola_5c7d24bb19976ca87e8f8bbb 5")
        sys.exit(1)

    candidate_id = sys.argv[1]
    num_articles = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    matcher.print_recommendations(candidate_id, num_articles=num_articles)


if __name__ == "__main__":
    main()
