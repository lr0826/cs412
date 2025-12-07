# File: urls.py
# Author: Run Liu (lr0826@bu.edu), 11/29/2025
# Description: The urls python file for the nba fantasy team final project
from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),

    # Players
    path("players/", views.PlayerListView.as_view(), name="player_list"),
    path("players/create/", views.PlayerCreateView.as_view(), name="player_create"),
    path("players/<int:pk>/", views.PlayerDetailView.as_view(), name="player_detail"),
    path("players/<int:pk>/edit/", views.PlayerUpdateView.as_view(), name="player_update"),
    path("players/<int:pk>/delete/", views.PlayerDeleteView.as_view(), name="player_delete"),


    # Fantasy teams
    path("teams/", views.FantasyTeamListView.as_view(), name="team_list"),
    path("teams/<int:pk>/", views.FantasyTeamDetailView.as_view(), name="team_detail"),
    path("teams/create/", views.FantasyTeamCreateView.as_view(), name="team_create"),
    path("teams/<int:pk>/edit/", views.FantasyTeamUpdateView.as_view(), name="team_update"),
    path("teams/<int:pk>/delete/", views.FantasyTeamDeleteView.as_view(), name="team_delete"),
     path("teams/<int:team_id>/add-player/", views.TeamMembershipCreateView.as_view(),
         name="team_add_player"),
    path("memberships/<int:pk>/delete/", views.TeamMembershipDeleteView.as_view(),
         name="membership_delete"),

    # Matchups
    path("matchups/", views.MatchupListView.as_view(), name="matchup_list"),
    path("matchups/<int:pk>/", views.MatchupDetailView.as_view(), name="matchup_detail"),

    path("matchups/create/", views.MatchupCreateView.as_view(), name="matchup_create"),
    path("matchups/<int:pk>/edit/", views.MatchupUpdateView.as_view(), name="matchup_update"),
    path("matchups/<int:pk>/delete/", views.MatchupDeleteView.as_view(), name="matchup_delete"),
    path("matchups/<int:pk>/simulate/", views.simulate_matchup, name="matchup_simulate"),
    path("matchups/<int:pk>/simulate-series/",
     views.simulate_series,
     name="matchup_simulate_series"),
]
