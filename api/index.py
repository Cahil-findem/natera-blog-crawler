"""
Vercel serverless entry point for Natera Blog Crawler
"""

import sys
from pathlib import Path

# Add parent directory to path to import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app

# Export the Flask app for Vercel
# Vercel looks for a variable that can handle requests
handler = app
