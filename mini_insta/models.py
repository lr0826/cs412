# File: models.py
# Author: Run Liu (lr0826@bu.edu), 9/23/2025
# Description: The models python file for the mini_insta application
from django.db import models

# Create your models here.
class Profile(models.Model):
    ''' model the data attributes of an individual user.'''
    username = models.TextField(blank=True)
    display_name = models.TextField(blank=True)
    profile_image_url = models.URLField(blank=True)
    bio_text = models.TextField(blank=True)
    join_date = models.TextField(blank=True)
    def __str__(self):
        ''' return the string representation of this model instance '''
        return f'{self.display_name}'
