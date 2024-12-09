#!/bin/bash

# Download model from Azure Blob Storage
python manage.py shell -c "from core.livenews.model_utils import download_model_from_blob; download_model_from_blob()"

# Make migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn --bind=0.0.0.0:8000 FakeNewsDetectorAPI.wsgi:application