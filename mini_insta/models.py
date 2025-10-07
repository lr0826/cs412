# File: models.py
# Author: Run Liu (lr0826@bu.edu), 9/23/2025
# Description: The models python file for the mini_insta application
from django.db import models
from django.urls import reverse
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
    def get_absolute_url(self):
        ''' return to the post url to display '''
        return reverse("show_post", kwargs={'pk':self.pk})
class Photo(models.Model):
    ''' model the data attributes of an image associated with a Post '''
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image_url = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    image_file = models.ImageField(blank=True)
    def __str__(self):
        ''' return the string representation of this Photo instance '''
        if self.image_file:
            return self.image_file.name
        else:
            return f'{self.image_url}'
    def get_image_url(self):
        ''' return the URL to the image. This URL will either be the URL stored 
        in the image_url attribute (if it exists), or else the URL to 
        the image_file attribute, i.e., image_file.url. '''
        if self.image_file:
            return self.image_file.url
        else:
            return self.image_url
        




