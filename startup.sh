#!/bin/bash

# Enable debug output
set -x

# Log output to a file
exec > >(tee -i /var/log/startup.log) 2>&1

echo "Starting deployment script..."

# Ensure Python virtual environment exists
echo "Setting up virtual environment..."
if [ ! -d "antenv" ]; then
    python -m venv antenv
fi

# Activate the virtual environment
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
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. Exiting."
    exit 1
fi

# Download model from Azure Blob Storage
echo "Downloading model..."
python manage.py shell -c "from core.livenews.model_utils import download_model_from_blob; download_model_from_blob()"
if [ $? -ne 0 ]; then
    echo "Model download failed. Exiting."
    exit 1
fi

# Run database migrations
echo "Running migrations..."
python manage.py makemigrations && python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Database migration failed. Exiting."
    exit 1
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
    echo "Collecting static files failed. Exiting."
    exit 1
fi

# Start Gunicorn server
echo "Starting Gunicorn..."
gunicorn --bind=0.0.0.0:8000 --workers=3 --log-level debug FakeNewsDetectorAPI.wsgi:application
if [ $? -ne 0 ]; then
    echo "Failed to start Gunicorn. Exiting."
    exit 1
fi