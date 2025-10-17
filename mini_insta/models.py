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
    def get_absolute_url(self):
        ''' return to the profile url to display '''
        return reverse("show_profile", kwargs={'pk':self.pk})
    def get_followers(self):
        """
        Return a list of Profile objects who follow THIS profile.
        Uses: Follow.objects.filter(profile=self)
        """
        follows = Follow.objects.filter(profile=self)           # Follow rows where I'm being followed
        return [f.follower_profile for f in follows]            # list of Profiles

    def get_num_followers(self):
        """Return the count of followers."""
        return Follow.objects.filter(profile=self).count()

    def get_following(self):
        """
        Return a list of Profile objects that THIS profile follows.
        Uses: Follow.objects.filter(follower_profile=self)
        """
        follows = Follow.objects.filter(follower_profile=self)  # Follow rows where I'm the follower
        return [f.profile for f in follows]                     # list of Profiles

    def get_num_following(self):
        """Return how many profiles this profile follows."""
        return Follow.objects.filter(follower_profile=self).count()
    def get_post_feed(self):
        """
        Posts from the profiles THIS profile follows, newest first.
        Reuses get_following() to get the followed Profile objects.
        """

        followed_profiles = self.get_following()          # list of profiles
        if not followed_profiles:
            return Post.objects.none()                    # empty QuerySet (nice for ListView)

        followed_ids = [p.pk for p in followed_profiles]
        return Post.objects.filter(profile_id__in=followed_ids).order_by("-timestamp")
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
    def get_all_comments(self):
        ''' retrive all comments on a Post '''
        comments = Comment.objects.filter(post=self)           # comments that is related to this post
        return comments
    def get_likes(self):
        """
        Return a list of Like objects for this Post.
        Uses the Django ORM explicitly (Like.objects.filter(...)).
        """
        likes = Like.objects.filter(post=self)
        return likes
    def get_num_likes(self):
        '''  Return the number of likes on this Post (int).
        '''
        count = Like.objects.filter(post=self).count()
        return count
    
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
class Follow(models.Model):
    '''encapsulates the idea of an edge connecting two nodes within the social network'''
    timestamp = models.DateTimeField(auto_now=True)
    profile = models.ForeignKey(
        "Profile",
        on_delete=models.CASCADE,
        related_name="profile"             # reverse accessor: who follows me
    )
    follower_profile = models.ForeignKey(
        "Profile",
        on_delete=models.CASCADE,
        related_name="follower_profile"    # reverse accessor: who I follow
    )
    def __str__(self):
        # Show readable names in admin/list pages
        who = self.follower_profile.display_name
        whom = self.profile.display_name
        return f"{who} follows {whom}"
class Comment(models.Model):
    '''encapsulates the idea of one Profile providing a response or commentary on a Post.'''
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    text = models.TextField(blank=False)
    def __str__(self):
        # view this Comment as a string representation
        return f"{self.text}"

class Like(models.Model):
    '''  encapsulates the idea of one Profile providing approval of a Post. '''
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    def __str__(self):
        # view this like as a string representation
        return f"{self.post.caption} liked by {self.profile.username}"

