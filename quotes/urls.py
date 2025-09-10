# File: urls.py
# Author: Run Liu (lr0826@bu.edu), 9/9/2025
# Description: The url python file for the quotes application

from django.urls import path
from django.conf import settings
from . import views

# URL patterns specific to the quotes app:
urlpatterns = [
    path(r'', views.quote, name="home"),
    path(r'quote', views.quote, name="quote_page"),
    path(r'about', views.about, name="about_page"),
    path(r'show_all', views.show_all, name="show_all_page"),
]