#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# python manage.py runserver
gunicorn msa.wsgi:application