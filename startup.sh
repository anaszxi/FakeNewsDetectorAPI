#!/bin/bash

# Navigate to the project directory
cd /home/site/wwwroot

# Set up the environment
export DJANGO_SETTINGS_MODULE=your_project_name.settings
export PYTHONPATH=$(pwd)

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Start the Gunicorn server
echo "Starting Gunicorn server..."
gunicorn your_project_name.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 60
