# File: views.py
# Author: Run Liu (lr0826@bu.edu), 9/23/2025
# Description: The view python file for the mini-insta application
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Profile, Post
# Create your views here.

class ProfileListView(ListView): 
    ''' a class-based view called ProfileListView, which inherits from the generic
    ListView. Use this view to obtain data for all Profile records, 
    and to delegate work to a template called show_all_profiles.html 
    to display all Profiles.'''
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"

class ProfileDetailView(DetailView):
    ''' obtain data for one Profile record, and to delegate work to 
    a template called show_profile.html to display that Profile.'''
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"
class PostDetailView(DetailView):
    ''' view function to display a single Post. '''
    model = Post
    template_name = "mini_insta/show_post.html"
    context_object_name = "post"