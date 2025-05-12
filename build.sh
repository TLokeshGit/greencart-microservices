#!/usr/bin/env bash

echo "🚀 Installing dependencies..."
pip install --upgrade pip
pip install -r django_backend/requirements.txt

# ✅ Set PYTHONPATH so Python can find django_backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)/django_backend"

# ✅ Set settings path
export DJANGO_SETTINGS_MODULE=django_backend.settings
echo "Using DJANGO_SETTINGS_MODULE: [$DJANGO_SETTINGS_MODULE]"

echo "⚙️ Applying migrations..."
python django_backend/manage.py migrate

echo "📦 Collecting static files..."
python django_backend/manage.py collectstatic --noinput
