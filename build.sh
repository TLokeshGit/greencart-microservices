#!/usr/bin/env bash

echo "🚀 Installing dependencies..."
pip install --upgrade pip
pip install -r django_backend/requirements.txt

export DJANGO_SETTINGS_MODULE=settings
echo "Using DJANGO_SETTINGS_MODULE: [$DJANGO_SETTINGS_MODULE]"

echo "⚙️ Applying migrations..."
python django_backend/manage.py migrate

echo "📦 Collecting static files..."
python django_backend/manage.py collectstatic --noinput
