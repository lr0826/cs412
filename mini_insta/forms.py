# File: forms.py
# Author: Run Liu (lr0826@bu.edu), 9/30/2025
# Description: The forms python file for the mini-insta application
from django import forms
from .models import *

class CreatePostForm(forms.ModelForm):
    ''' A form to add a post to datebase '''
    class Meta:
        ''' associate this form with a model in our database '''
        model = Post
        fields = ['caption']
        
class UpdateProfileForm(forms.ModelForm):
    ''' a form to handle updating a profile '''
    class Meta:
        ''' associate this form with a model in our database '''
        model = Profile
        fields = ['display_name', 'profile_image_url', 'bio_text'] # three fields that we need to update

class UpdatePostForm(forms.ModelForm):
    ''' a form to handle updating a profile '''
    class Meta:
        ''' associate this form with a model in our database '''
        model = Post
        fields = ['caption'] # only update the caption
class CreateProfileForm(forms.ModelForm):
    '''a from to handle creation of a profile'''
    class Meta:
        model = Profile
        fields = ['username', 'display_name', 'bio_text', 'profile_image_url']