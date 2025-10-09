# File: views.py
# Author: Run Liu (lr0826@bu.edu), 9/23/2025
# Description: The view python file for the mini-insta application
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import *
from .forms import CreatePostForm, UpdateProfileForm, UpdatePostForm

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
    """Create a new Post for a given Profile, then attach any uploaded Photos."""
    form_class = CreatePostForm
    template_name = "mini_insta/create_post_form.html"

    def get_context_data(self, **kwargs):
        """Add the parent Profile to the template context (no get_object_or_404)."""
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']                 
        profile = Profile.objects.get(pk=pk)   
        context['profile'] = profile
        context['hide_create_button'] = True
        return context

    def form_valid(self, form):
        """Attach FK (Profile) before saving, then create Photo rows for uploaded files."""
        print(f"CreatePostView.form_valid: form.cleaned_data={form.cleaned_data}")

        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)   
        form.instance.profile = profile        

        # Save the Post (self.object becomes the saved Post)
        response = super().form_valid(form)
        files = self.request.FILES.getlist("files")
        print("DEBUG CreatePostView:", "num_files=", len(files), "names=", [f.name for f in files])

        # Create Photo objects from uploaded files (input name="files")
        files = self.request.FILES.getlist('files')
        for f in files:
            Photo.objects.create(post=self.object, image_file=f)

        return response


    def get_success_url(self):
        """Where to go after creating the Post (adjust to your URL names)."""
        # Example: go to the newly created Post's page
        return reverse('show_post', kwargs={'pk': self.object.pk})
class UpdateProfileView(UpdateView):
    ''' view class to handle update of profile based on its PK '''
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_insta/update_profile_form.html"
    
class DeletePostView(DeleteView):
    ''' View class to delete a post on a profile '''
    model = Post
    template_name = "mini_insta/delete_post_form.html"
    def get_success_url(self):
        ''' Return the URL to redirect to after a successful delete. '''
        #find the pk for this post
        pk = self.kwargs['pk']
        post = Post.objects.get(pk=pk)
        profile = post.profile
        return reverse('show_profile', kwargs={'pk':profile.pk})
class UpdatePostView(UpdateView):
    ''' view class to handle update of post based on its PK '''
    model = Post
    form_class = UpdatePostForm
    template_name = "mini_insta/update_post_form.html"