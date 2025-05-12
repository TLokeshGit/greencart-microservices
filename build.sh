#!/usr/bin/env bash

echo "🚀 Installing dependencies..."
pip install --upgrade pip
pip install -r django_backend/requirements.txt

# ✅ Explicitly set settings module
export DJANGO_SETTINGS_MODULE=django_backend.settings

echo "⚙️ Applying migrations..."
python django_backend/manage.py migrate

echo "📦 Collecting static files..."
python django_backend/manage.py collectstatic --noinput
