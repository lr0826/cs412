# File: views.py
# Author: Run Liu (lr0826@bu.edu), 9/23/2025
# Description: The view python file for the mini-insta application
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import *
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse
# Create your views here.

class ProfileListView(ListView): 
    ''' a class-based view called ProfileListView, which inherits from the generic
    ListView. Use this view to obtain data for all Profile records, 
    and to delegate work to a template called show_all_profiles.html 
    to display all Profiles.'''
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            vp = Profile.objects.filter(user=self.request.user).order_by("id").first()
            ctx["viewer_profile"] = vp
        return ctx

    
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
        return (Profile.objects
            .filter(user=self.request.user)
            .order_by("id")
            .first())

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
        ctx["viewer_profile"] = self.viewer_profile
        return ctx

class ProfileDetailView(DetailView):
    ''' obtain data for one Profile record, and to delegate work to 
    a template called show_profile.html to display that Profile.'''
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        viewer = None
        if self.request.user.is_authenticated:
            viewer = Profile.objects.filter(user=self.request.user).order_by("id").first()
        ctx["viewer_profile"] = viewer
        ctx["is_following"] = (
            Follow.objects.filter(profile=self.object, follower_profile=viewer).exists()
            if viewer else False
        )

        return ctx
class PostDetailView(DetailView):
    ''' view function to display a single Post. '''
    model = Post
    template_name = "mini_insta/show_post.html"
    context_object_name = "post"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            vp = Profile.objects.filter(user=self.request.user).order_by("id").first()
            ctx["viewer_profile"] = vp
        return ctx
    

class CreatePostView(LoginProfileMixin, CreateView):
    """Create a new Post for a given Profile, then attach any uploaded Photos."""
    form_class = CreatePostForm
    template_name = "mini_insta/create_post_form.html"
    def get_context_data(self, **kwargs):
        """Add the parent Profile to the template context."""
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = self.viewer_profile
        ctx["hide_create_button"] = True
        if self.request.user.is_authenticated:
            vp = Profile.objects.filter(user=self.request.user).order_by("id").first()
            ctx["viewer_profile"] = vp
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
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            vp = Profile.objects.filter(user=self.request.user).order_by("id").first()
            ctx["viewer_profile"] = vp
        return ctx

class ShowFollowingDetailView(DetailView):
    """Detail view for a Profile that shows who this profile follows."""
    model = Profile
    template_name = "mini_insta/show_following.html"
    context_object_name = "profile"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            vp = Profile.objects.filter(user=self.request.user).order_by("id").first()
            ctx["viewer_profile"] = vp
        return ctx
class PostFeedListView(LoginProfileMixin, ListView):
    ''' List View for the post feed '''
    template_name = "mini_insta/show_feed.html"
    context_object_name = "posts"

    def get_queryset(self):
        # Show posts from profiles the viewer follows, newest first
        return self.viewer_profile.get_post_feed()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        posts = ctx["posts"]
        liked_ids = Like.objects.filter(
            profile=self.viewer_profile,
            post__in=posts
        ).values_list("post_id", flat=True)
        # Use list so Django template “in” works reliably
        ctx["liked_post_ids"] = list(liked_ids)
        ctx["profile"] = self.viewer_profile
        ctx["viewer_profile"] = self.viewer_profile
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
        ctx["viewer_profile"] = self.viewer_profile
        return ctx
class CreateProfileView(CreateView):
    ''' A view to show/process the registration form to create a new User '''
    model = Profile
    form_class = CreateProfileForm
    template_name = "mini_insta/create_profile_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # If POST, bind the user form so errors show; else unbound form
        if self.request.method == "POST":
            ctx["user_form"] = UserCreationForm(self.request.POST)
        else:
            ctx["user_form"] = UserCreationForm()
        return ctx

    def form_valid(self, form):
        """
        1) Rebuild UserCreationForm from POST
        2) If valid: save new User, log them in, attach to Profile, then super().form_valid(form)
        3) If invalid: re-render with errors for BOTH forms
        """
        user_form = UserCreationForm(self.request.POST)

        if not user_form.is_valid():
            # Model form is valid (we're in form_valid), but user form is not.
            # Re-render the template with both forms + errors.
            context = self.get_context_data()
            context["form"] = form   # the valid profile form (still bound)
            context["user_form"] = user_form  # invalid user form with errors
            return render(self.request, self.template_name, context)

        # 1) Create the Django User
        user = user_form.save()

        # 2) Log the user in
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")

        # 3) Attach this user to the Profile and save via the normal CreateView flow
        form.instance.user = user
        return super().form_valid(form)

    def get_success_url(self):
        # After creating the profile, go to its detail page
        return self.object.get_absolute_url()

class FollowCreateView(LoginProfileMixin, TemplateView):
    template_name = "mini_insta/blank.html"  # never rendered

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        self.viewer_profile = self.get_viewer_profile()
        if not self.viewer_profile:
            return redirect(reverse("create_profile"))

        target = Profile.objects.get(pk=kwargs["pk"])
        if target.pk != self.viewer_profile.pk:  # block self-follow
            Follow.objects.get_or_create(
                profile=target,
                follower_profile=self.viewer_profile
            )
        nxt = request.POST.get("next") or request.GET.get("next")
        return redirect(nxt or reverse("show_profile", kwargs={"pk": target.pk}))


class FollowDeleteView(LoginProfileMixin, TemplateView):
    template_name = "mini_insta/blank.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        self.viewer_profile = self.get_viewer_profile()
        if not self.viewer_profile:
            return redirect(reverse("create_profile"))

        target = Profile.objects.get(pk=kwargs["pk"])
        Follow.objects.filter(profile=target, follower_profile=self.viewer_profile).delete()
        nxt = request.POST.get("next") or request.GET.get("next")
        return redirect(nxt or reverse("show_profile", kwargs={"pk": target.pk}))


class LikeCreateView(LoginProfileMixin, TemplateView):
    template_name = "mini_insta/blank.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        self.viewer_profile = self.get_viewer_profile()
        if not self.viewer_profile:
            return redirect(reverse("create_profile"))

        post = Post.objects.get(pk=kwargs["pk"])
        if post.profile_id != self.viewer_profile.pk:  # block self-like
            Like.objects.get_or_create(post=post, profile=self.viewer_profile)

        nxt = request.POST.get("next") or request.GET.get("next")
        return redirect(nxt or reverse("show_post", kwargs={"pk": post.pk}))


class LikeDeleteView(LoginProfileMixin, TemplateView):
    template_name = "mini_insta/blank.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        self.viewer_profile = self.get_viewer_profile()
        if not self.viewer_profile:
            return redirect(reverse("create_profile"))

        post = Post.objects.get(pk=kwargs["pk"])
        Like.objects.filter(post=post, profile=self.viewer_profile).delete()

        nxt = request.POST.get("next") or request.GET.get("next")
        return redirect(nxt or reverse("show_post", kwargs={"pk": post.pk}))
# new view
class MyProfileDetailView(LoginProfileMixin, DetailView):
    """Show the logged-in user's own Profile at /mini_insta/profile/"""
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        # LoginProfileMixin already set self.viewer_profile
        return self.viewer_profile
