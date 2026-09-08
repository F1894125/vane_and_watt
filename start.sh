#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# echo "Running makemigrations..."
# python manage.py makemigrations
# This script should migrate but not make migrations as migrations
# generated in the container are not saved back into the project.

echo "Running migrations..."
python manage.py migrate

echo "Running checks..."
python manage.py check

echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000