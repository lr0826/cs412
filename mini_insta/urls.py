# File: urls.py
# Author: Run Liu (lr0826@bu.edu), 9/23/2025
# Description: The url python file for the mini-insta application
from django.urls import path
from django.conf import settings
from .views import *

urlpatterns = [
    path('', ProfileListView.as_view(), name="show_all_profiles"),
    path('profile/<int:pk>', ProfileDetailView.as_view(), name='show_profile'),
    path('post/<int:pk>', PostDetailView.as_view(), name='show_post'),
    path('profile/<int:pk>/create_post', CreatePostView.as_view(), name='create_post'),
    path('profile/<int:pk>/update', UpdateProfileView.as_view(), name='update_profile'),
    path('post/<int:pk>/delete', DeletePostView.as_view(), name='delete_post'),
    path('post/<int:pk>/update', UpdatePostView.as_view(), name='update_post'),
] 