# urls.py for dadjokes application
from django.urls import path
from . import views

app_name = "dadjokes"

urlpatterns = [
    path("", views.random_pair, name="home"),                 # ''
    path("/random", views.random_pair, name="random"),        # 'random'
    path("/jokes", views.jokes_list, name="jokes_list"),      # 'jokes'
    path("/joke/<int:pk>", views.joke_detail, name="joke_detail"),  # 'joke/<int:pk>'
    path("/pictures", views.pictures_list, name="pictures_list"),    # 'pictures'
    path("/picture/<int:pk>", views.picture_detail, name="picture_detail"),  # 'picture/<int:pk>'

    # API views
    path("/api", views.RandomJokeAPIView.as_view(), name="api_home"),                 # 'api/'
    path("/api/random", views.RandomJokeAPIView.as_view(), name="api_random"),        # 'api/random'
    path("/api/jokes", views.JokeListCreateAPIView.as_view(), name="api_jokes"),      # 'api/jokes'
    path("/api/joke/<int:pk>", views.JokeDetailAPIView.as_view(), name="api_joke"),   # 'api/joke/<int:pk>'
    path("/api/pictures", views.PictureListAPIView.as_view(), name="api_pictures"),   # 'api/pictures'
    path("/api/picture/<int:pk>", views.PictureDetailAPIView.as_view(), name="api_picture"),  # 'api/picture/<int:pk>'
    path("/api/random_picture", views.RandomPictureAPIView.as_view(), name="api_random_picture"),
]