# File: urls.py
# Author: Run Liu (lr0826@bu.edu), 9/23/2025
# Description: The url python file for the mini-insta application
from django.urls import path
from django.conf import settings
from .views import ProfileListView, ProfileDetailView

urlpatterns = [
    path('', ProfileListView.as_view(), name="show_all_profiles"),
    path('profile/<int:pk>', ProfileDetailView.as_view(), name='show_profile'),
]