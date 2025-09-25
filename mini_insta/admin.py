# File: admin.py
# Author: Run Liu (lr0826@bu.edu), 9/23/2025
# Description: The admin python file for the mini_insta application
# Register your models here.
from django.contrib import admin

from .models import Profile
admin.site.register(Profile)