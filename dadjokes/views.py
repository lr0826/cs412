# views function for the dadjokes application

from django.shortcuts import render
from django.http import Http404
from .models import Joke, Picture


def get_random_joke_and_picture():
    ''' helper funciton to get random joke or picture '''
    joke = Joke.objects.order_by("?").first()
    picture = Picture.objects.order_by("?").first()
    return joke, picture


def random_pair(request):
    """Show one random Joke + one random Picture."""
    joke, picture = get_random_joke_and_picture()
    context = {
        "joke": joke,
        "picture": picture,
    }
    return render(request, "dadjokes/random_pair.html", context)


def jokes_list(request):
    """Show all jokes (no images)."""
    jokes = Joke.objects.all().order_by("-created_at")
    return render(request, "dadjokes/jokes_list.html", {"jokes": jokes})


def joke_detail(request, pk):
    """Show one joke by primary key (no get_object_or_404)."""
    try:
        joke = Joke.objects.get(pk=pk)
    except Joke.DoesNotExist:
        raise Http404("Joke not found")
    return render(request, "dadjokes/joke_detail.html", {"joke": joke})


def pictures_list(request):
    """Show all pictures (no jokes)."""
    pictures = Picture.objects.all().order_by("-created_at")
    return render(request, "dadjokes/pictures_list.html", {"pictures": pictures})


def picture_detail(request, pk):
    
    """Show one picture by primary key."""
    try:
        picture = Picture.objects.get(pk=pk)
    except Picture.DoesNotExist:
        raise Http404("Picture not found")
    return render(request, "dadjokes/picture_detail.html", {"picture": picture})


# ===========================
# API VIEWS
# ===========================
from rest_framework import generics
from .serializers import *
class RandomJokeAPIView(generics.RetrieveAPIView):
    """
    'api/' and 'api/random' - return ONE random Joke as JSON.
    """
    serializer_class = JokeSerializer

    def get_object(self):
        joke = Joke.objects.order_by("?").first()
        if joke is None:
            raise Http404("No jokes available")
        return joke


class JokeListCreateAPIView(generics.ListCreateAPIView):
    """
    'api/jokes' - GET: all jokes, POST: create a new joke.
    """
    queryset = Joke.objects.all().order_by("-created_at")
    serializer_class = JokeSerializer


class JokeDetailAPIView(generics.RetrieveAPIView):
    """
    'api/joke/<int:pk>' - return one joke by primary key.
    """
    queryset = Joke.objects.all()
    serializer_class = JokeSerializer
    # lookup_field = "pk"  # default, so this line is optional


class PictureListAPIView(generics.ListAPIView):
    """
    'api/pictures' - GET: all pictures.
    """
    queryset = Picture.objects.all().order_by("-created_at")
    serializer_class = PictureSerializer


class PictureDetailAPIView(generics.RetrieveAPIView):
    """
    'api/picture/<int:pk>' - return one picture by primary key.
    """
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer

class RandomPictureAPIView(generics.RetrieveAPIView):
    """
    'api/random_picture' - return ONE random Picture as JSON.
    """
    serializer_class = PictureSerializer

    def get_object(self):
        picture = Picture.objects.order_by("?").first()
        if picture is None:
            raise Http404("No pictures available")
        return picture
