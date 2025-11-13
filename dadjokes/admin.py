# File: admin.py
# Author: Run Liu (lr0826@bu.edu), 10/18/2025
# Description: The admin python file for the dadjokes application
# Register your models here.
from django.contrib import admin

from .models import *
admin.site.register(Joke)
admin.site.register(Picture)
