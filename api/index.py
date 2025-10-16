"""
Vercel serverless function entry point
"""
import sys
from os.path import dirname, abspath

# Add parent directory to Python path
root_dir = dirname(dirname(abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    # Import the Flask app
    from app import app as application

    # Vercel will use this as the serverless function handler
    app = application
except Exception as e:
    # If imports fail, create a minimal Flask app to show the error
    from flask import Flask, jsonify
    app = Flask(__name__)

    @app.route('/')
    def error():
        return jsonify({
            'error': 'Failed to initialize application',
            'details': str(e),
            'type': type(e).__name__
        }), 500

    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
