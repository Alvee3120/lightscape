#!/usr/bin/env bash
set -o errexit

npm ci
npm run build:css

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
