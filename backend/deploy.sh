#!/bin/bash

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export MEXC_API_KEY="your_api_key"
export MEXC_API_SECRET="your_api_secret"
export SECRET_KEY="your_secret_key"
export DATABASE_URL="sqlite:///./scheduled_trader.db"

# Start the FastAPI application with Gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 