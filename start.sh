#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Running makemigrations..."
python manage.py makemigrations

echo "Running migrate..."
python manage.py migrate

echo "Running check..."
python manage.py check

echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000