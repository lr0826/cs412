# File: models.py
# Author: Run Liu (lr0826@bu.edu), 9/23/2025
# Description: The models python file for the dadjokes application
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
class Joke(models.Model):
    ''' the joke model that stores store the text of a joke, the name of the contributor, 
    and the timestamp of when it was created '''
    
    text = models.TextField()
    contributor_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)  # set automatically on create

    def __str__(self):
        # show a short preview 
        return self.text[:50] + ("..." if len(self.text) > 50 else "")


class Picture(models.Model):
    image_url = models.URLField()
    contributor_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)  # set automatically on create

    def __str__(self):
        return self.image_url

