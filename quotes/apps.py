# File: apps.py
# Author: Run Liu (lr0826@bu.edu), 9/9/2025
# Description: The apps python file for the quotes application
from django.apps import AppConfig


class QuotesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quotes'
