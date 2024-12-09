#!/bin/bash

# Enable debug output
set -x

echo "Starting deployment script..."

# Create and activate virtual environment (cross-platform)
echo "Setting up virtual environment..."
python -m venv antenv
if [ -f antenv/Scripts/activate ]; then
    # Windows
    . antenv/Scripts/activate
else
    # Linux/Mac
    . antenv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Download model from Azure Blob Storage
echo "Downloading model..."
python manage.py shell -c "from core.livenews.model_utils import download_model_from_blob; download_model_from_blob()"

# Make migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn with debug logging
echo "Starting Gunicorn..."
gunicorn --bind=0.0.0.0:8000 --log-level debug FakeNewsDetectorAPI.wsgi:application