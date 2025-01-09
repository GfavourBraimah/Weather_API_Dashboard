#!/bin/bash

# Navigate to the existing weather_dashboard directory
cd weather_dashboard

# Create subdirectories
mkdir -p src
mkdir -p tests
mkdir -p data

# Create files
touch src/__init__.py
touch src/weather_dashboard.py
touch .env
touch .gitignore
touch requirements.txt

echo "Project structure created successfully."