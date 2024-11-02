@echo off
setlocal enabledelayedexpansion

echo Initializing New Python Virtual Environment
python -m venv venv

echo Activating Virtual Environment
call venv\Scripts\activate.bat

echo Installing Django
pip install Django

echo Installing mysqlclient
pip install mysqlclient

echo Installing Dotenv
pip install python-dotenv

echo Installing Pillow
pip install pillow

echo Installing BeautifulSoup
pip install beautifulsoup4

echo Installing TinyMCE for Django
pip install django-tinymce

echo Installing Requests
pip install requests

echo Installing Faker
pip install Faker

echo Installing Django Ratelimit
pip install django-ratelimit

echo Deactivating Virtual Environment
deactivate

echo To run the virtual environment, simply run: call venv\Scripts\activate.bat
