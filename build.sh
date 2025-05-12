#!/usr/bin/env bash

echo "🚀 Installing dependencies..."
pip install --upgrade pip
pip install -r django_backend/requirements.txt

echo "⚙️ Applying migrations..."
python django_backend/manage.py migrate

echo "📦 Collecting static files..."
python django_backend/manage.py collectstatic --noinput
