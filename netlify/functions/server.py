"""
Netlify serverless function handler for FastAPI app
"""
import sys
import os
from mangum import Mangum

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from main import app

# Wrap FastAPI app with Mangum for AWS Lambda/Netlify compatibility
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """AWS Lambda handler for Netlify Functions"""
    return handler(event, context)

