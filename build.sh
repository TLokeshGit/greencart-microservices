#!/usr/bin/env bash

echo "🚀 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "⚙️ Applying migrations..."
python manage.py migrate

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput
