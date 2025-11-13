"""
Vercel serverless function entry point for FastAPI app
"""
import sys
import os

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Export the app for Vercel
handler = app

