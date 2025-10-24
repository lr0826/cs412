# File: views.py
# Author: Run Liu (lr0826@bu.edu), 9/23/2025
# Description: The view python file for the mini-insta application
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import *
from .forms import CreatePostForm, UpdateProfileForm, UpdatePostForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
# Create your views here.

class ProfileListView(ListView): 
    ''' a class-based view called ProfileListView, which inherits from the generic
    ListView. Use this view to obtain data for all Profile records, 
    and to delegate work to a template called show_all_profiles.html 
    to display all Profiles.'''
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"

    
class LoginProfileMixin(LoginRequiredMixin):
    """
    Require login and expose:
      - self.viewer_profile: Profile for self.request.user
      - context['profile']: same Profile for templates (nav/footer)
    Helpers:
      - get_viewer_profile()
      - get_target_profile()
      - require_owner(obj)
    """
    login_url = "login"
    def get_login_url(self):
        return reverse("login")
    # ---- core helpers ----
    def get_viewer_profile(self):
        return Profile.objects.get(user=self.request.user)

    def get_target_profile(self):
        """Use URL pk if present; otherwise fall back to the viewer."""
        pk = self.kwargs.get("pk")
        if pk is not None:
            return Profile.objects.get(pk=pk)
        return getattr(self, "viewer_profile", self.get_viewer_profile())

    def require_owner(self, obj):
        """Ensure the current user owns obj (which must have .profile)."""
        owner = getattr(obj, "profile", None)
        if owner is None or owner.user_id != self.request.user.id:
            raise PermissionDenied("You do not have permission to modify this object.")

    def dispatch(self, request, *args, **kwargs):
        # Enforce login FIRST (so AnonymousUser never reaches helpers)
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Set viewer_profile BEFORE calling super().dispatch()
        self.viewer_profile = self.get_viewer_profile()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Provide 'profile' for nav/footer (always available after dispatch)
        ctx["profile"] = self.viewer_profile
        return ctx

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
    

class CreatePostView(LoginProfileMixin, CreateView):
    """Create a new Post for a given Profile, then attach any uploaded Photos."""
    form_class = CreatePostForm
    template_name = "mini_insta/create_post_form.html"
    def get_context_data(self, **kwargs):
        """Add the parent Profile to the template context."""
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = self.viewer_profile
        ctx["hide_create_button"] = True
        return ctx

    def form_valid(self, form):
        """Attach FK (Profile) before saving, then create Photo rows for uploaded files."""
        form.instance.profile = self.viewer_profile
        response = super().form_valid(form)

        files = self.request.FILES.getlist("files")
        print("DEBUG CreatePostView:", "num_files=", len(files), "names=", [f.name for f in files])
        for f in files:
            Photo.objects.create(post=self.object, image_file=f)

        return response


    def get_success_url(self):
        """Where to go after creating the Post (adjust to your URL names)."""
        # Example: go to the newly created Post's page
        return reverse('show_post', kwargs={'pk': self.object.pk})
class UpdateProfileView(LoginProfileMixin, UpdateView):
    ''' view class to handle update of profile based on its PK '''
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_insta/update_profile_form.html"
    def get_object(self, queryset=None):
        ''' get profile with out pk '''
        return self.viewer_profile
        
        
    
class DeletePostView(LoginProfileMixin, DeleteView):
    ''' View class to delete a post on a profile '''
    model = Post
    template_name = "mini_insta/delete_post_form.html"
    def get_queryset(self):
        ''' filter the queryset by profile '''
        return Post.objects.filter(profile__user=self.request.user)
    def get_success_url(self):
        ''' updated get success url function that does not rely on pk '''
        return reverse("show_profile", kwargs={"pk": self.object.profile_id})
class UpdatePostView(LoginProfileMixin, UpdateView):
    ''' view class to handle update of post based on its PK '''
    model = Post
    form_class = UpdatePostForm
    template_name = "mini_insta/update_post_form.html"
    def get_queryset(self):
        ''' filter the queryset by profile '''
        return Post.objects.filter(profile__user=self.request.user)
    def get_success_url(self):
        ''' updated get success url function that does not rely on pk '''
        return reverse("show_profile", kwargs={"pk": self.object.profile_id})

class ShowFollowersDetailView(DetailView):
    """Detail view for a Profile that shows its followers list."""
    model = Profile
    template_name = "mini_insta/show_followers.html"
    context_object_name = "profile"

class ShowFollowingDetailView(DetailView):
    """Detail view for a Profile that shows who this profile follows."""
    model = Profile
    template_name = "mini_insta/show_following.html"
    context_object_name = "profile"
class PostFeedListView(LoginProfileMixin, ListView):
    ''' List View for the post feed '''
    template_name = "mini_insta/show_feed.html"
    context_object_name = "posts"

    def get_queryset(self):
        # Show posts from profiles the viewer follows, newest first
        return self.viewer_profile.get_post_feed()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # profile for header/footer/nav
        ctx["profile"] = self.viewer_profile
        return ctx
class SearchView(LoginProfileMixin, ListView):
    ''' search view for the search function '''
    template_name = "mini_insta/search_results.html"
    context_object_name = "posts"

    def get(self, request, *args, **kwargs):
        self.query = (request.GET.get("q") or "").strip()
        if not self.query:
            # viewer_profile is set by the mixin before get() is called
            return render(request, "mini_insta/search.html", {"profile": self.viewer_profile})
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Post.objects.filter(caption__icontains=self.query).order_by("-timestamp")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.query
        p1 = Profile.objects.filter(username__icontains=self.query)
        p2 = Profile.objects.filter(display_name__icontains=self.query)
        p3 = Profile.objects.filter(bio_text__icontains=self.query)
        ctx["profiles"] = (p1 | p2 | p3).distinct()
        return ctx
