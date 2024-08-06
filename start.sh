#!/bin/bash

# Install required Python packages without using the cache
pip install --no-cache-dir -r requirements.txt

# Install a specific version of Flask
pip install Flask==2.3.2

# Set the FLASK_APP environment variable
export FLASK_APP=app.py

# Install Xvfb (X virtual framebuffer)
apt-get update && apt-get install -y xvfb

# Start Xvfb in the background
Xvfb :99 -screen 0 1024x768x24 &

# Set the DISPLAY environment variable to use Xvfb
export DISPLAY=:99

# Start the Flask application and stream logs to both file and stdout/stderr
python app.py 
