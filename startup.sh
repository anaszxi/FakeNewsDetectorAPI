#!/bin/bash

# Enable debug output
set -x

echo "Starting deployment script..."

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