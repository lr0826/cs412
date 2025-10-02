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