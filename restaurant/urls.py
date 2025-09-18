# File: urls.py
# Author: Run Liu (lr0826@bu.edu), 9/16/2025
# Description: The url python file for the restaurant application
from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path(r'main', views.main, name="main"),
    path(r'order', views.order, name="order"),
    path(r'confirmation', views.confirmation, name="confirmation"),
    
]