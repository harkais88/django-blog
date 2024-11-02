#!/bin/bash

set -e #Should exit on error

echo "Initializing New Python Virtual Environment"
python3 -m venv venv

echo "Activating Virtual Environment"
source venv/bin/activate

echo "Installing Django"
venv/bin/python -m pip install Django

echo "Install mysqlclient"
venv/bin/python -m pip install mysqlclient

echo "Installing Dotenv"
venv/bin/python -m pip install python-dotenv

echo "Installing Pillow"
venv/bin/python -m pip install pillow

echo "Installing BeautifulSoup"
venv/bin/python -m pip install beautifulsoup4

echo "Installing TinyMCE for Django"
venv/bin/python -m pip install django-tinymce

echo "Installing Requests"
venv/bin/python -m pip install requests

echo "Installing Faker"
venv/bin/python -m pip install Faker

echo "Installing Django Ratelimit"
venv/bin/python -m pip install django-ratelimit

echo "Deactivating Virtual Environment"
deactivate

echo "To run virtual environment, simply run source venv/bin/activate"