# filepath: /Users/lokesh/Desktop/ALL/greencart-microservices/build.sh
#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

echo "🚀 Installing dependencies..."
pip install --upgrade pip
pip install -r django_backend/requirements.txt

# ✅ Add this so Python knows where to find 'django_backend'
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "⚙️ Applying migrations..."
python django_backend/manage.py migrate --noinput

echo "📦 Collecting static files..."
python django_backend/manage.py collectstatic --noinput
