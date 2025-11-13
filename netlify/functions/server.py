"""
Netlify serverless function handler for FastAPI app
"""
import sys
import os

# Add parent directory to path to import main
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Initialize database before importing app
try:
    import database
    if database.DATABASE_URL:
        database.init_database()
except Exception as e:
    print(f"Database initialization warning: {e}")

from mangum import Mangum
from main import app

# Wrap FastAPI app with Mangum for AWS Lambda/Netlify compatibility
mangum_handler = Mangum(app, lifespan="off")

# Export handler for Netlify Functions
def handler(event, context):
    """AWS Lambda handler for Netlify Functions"""
    return mangum_handler(event, context)

