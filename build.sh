#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py makemigration

python manage.py migrate
python manage.py collectstatic 
python manage.py runserver 