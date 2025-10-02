# File: views.py
# Author: Run Liu (lr0826@bu.edu), 9/23/2025
# Description: The view python file for the mini-insta application
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import *
from .forms import CreatePostForm
from django.shortcuts import get_object_or_404

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
    

class CreatePostView(CreateView):
    ''' A view to handle creation of a new Post 
    displat the html form to user
    process the form submission and store the new post object'''
    form_class = CreatePostForm
    template_name =  "mini_insta/create_post_form.html"
    def get_context_data(self, **kwargs):
        ''' context data that provide access to the profile data '''
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = get_object_or_404(Profile, pk=self.kwargs["pk"])
        ctx["hide_create_button"] = True
        return ctx
    def form_valid(self, form):
        '''set FK by id without querying Profile'''
        # (a) attach the Profile to the Post before saving
        profile = get_object_or_404(Profile, pk=self.kwargs["pk"])
        form.instance.profile = profile

        # save the Post (self.object becomes the saved Post)
        response = super().form_valid(form)

        # (b) create a Photo from the extra image_url input
        image_url = (self.request.POST.get("image_url") or "").strip()
        if image_url:
            Photo.objects.create(post=self.object, image_url=image_url)

        return response