#!/bin/bash

# Enable debug output
set -x

# Log output to a file
exec > >(tee -i /var/log/startup.log) 2>&1

echo "Starting deployment script..."

# Environment setup
export PYTHONPATH=/home/site/wwwroot
export DJANGO_SETTINGS_MODULE=FakeNewsDetectorAPI.deployment

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. Exiting."
    exit 1
fi

# Create necessary directories
mkdir -p /home/site/wwwroot/staticfiles
mkdir -p /home/site/wwwroot/models

# ... (rest of your script - model download, migrations, collectstatic, Gunicorn) ...
