#!/bin/bash

# Make migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn --bind=0.0.0.0:8000 FakeNewsDetectorAPI.wsgi:application 