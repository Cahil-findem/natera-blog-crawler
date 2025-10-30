"""
Clear all news articles from the natera_news table
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
print("CLEAR NATERA NEWS TABLE")
print("=" * 80)

# Check how many articles exist
result = supabase.table('natera_news').select('id', count='exact').execute()
count = result.count if hasattr(result, 'count') else len(result.data)

print(f"\nFound {count} articles in natera_news table")

if count > 0:
    confirm = input(f"\n⚠️  Are you sure you want to DELETE all {count} articles? (yes/no): ")

    if confirm.lower() == 'yes':
        print("\nDeleting all articles...")

        # Delete all records
        # Note: Supabase doesn't have a direct "delete all" - we need to delete in batches
        # or use a filter that matches everything
        delete_result = supabase.table('natera_news').delete().neq('id', 0).execute()

        print(f"✅ Successfully deleted all articles from natera_news table!")
        print("\nYou can now run the crawler to populate with fresh data:")
        print("  python3 natera_news_crawler.py 50")
    else:
        print("\n❌ Deletion cancelled.")
else:
    print("\n✅ Table is already empty!")

print("\n" + "=" * 80)
