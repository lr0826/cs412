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
    def get_all_posts(self):
        ''' find and return all Posts for a given Profile. '''
        posts = Post.objects.filter(profile=self).order_by('-timestamp')
        return posts
class Post(models.Model):
    '''model the data attributes of an Instagram post'''
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    caption = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now=True)
    def __str__(self):
        ''' return the string representation of this Post instance '''
        return f'{self.caption}'
    def get_all_photos(self):
        ''' find and return all Photos for a given Post. '''
        photos = Photo.objects.filter(post=self)
        return photos
class Photo(models.Model):
    ''' model the data attributes of an image associated with a Post '''
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image_url = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now=True)
    def __str__(self):
        ''' return the string representation of this Photo instance '''
        return f'{self.image_url}'



