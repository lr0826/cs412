from django.urls import path
from . import views

urlpatterns = [
    # list page (home page of the app)
    path('', views.VoterListView.as_view(), name='voters'),

    # detail page for one voter
    path('voter/<int:pk>/', views.VoterDetailView.as_view(), name='voter'),
    path('graphs', views.GraphListView.as_view(), name='graphs'),
]
