# File: views.py
# Author: Run Liu (lr0826@bu.edu), 11/29/2025
# Description: The views python file for the nba fantasy team final project

from django.views.generic import *
from .models import *
from django.urls import reverse
from .forms import *
from django.shortcuts import get_object_or_404, redirect, render
import random
from django.db.models import Q

def _average_team_rating(team: FantasyTeam) -> float:
    """
    Compute the average overall rating for all players on a given fantasy team.

    This helper looks up all TeamMembership records for the team, collects the
    non-null overall_rating values from each related Player, and returns their
    arithmetic mean. If the team has no players or no ratings, a default
    rating of 50.0 is returned so that simulations can still run.
    """
    memberships = TeamMembership.objects.filter(team=team)
    ratings = [
        m.player.overall_rating
        for m in memberships
        if m.player.overall_rating is not None
    ]
    if not ratings:
        return 50.0
    return sum(ratings) / len(ratings)


def _simulate_single_game(home_team: FantasyTeam, away_team: FantasyTeam):
    """
    Simulate a single basketball game between two fantasy teams.

    Uses the average rating of each team, a rating_factor, and a home-court
    bonus to generate expected scores around 100 points, then samples actual
    scores from normal distributions. If the scores are tied, the home team
    is given one extra point. Returns a tuple:
        (home_score, away_score, winner_team)
    """
    home_rating = _average_team_rating(home_team)
    away_rating = _average_team_rating(away_team)

    rating_factor = 0.3
    home_court_bonus = 3.0  # home court advantage

    base_home = 100 + (home_rating - away_rating) * rating_factor + home_court_bonus
    base_away = 100 + (away_rating - home_rating) * rating_factor

    home_score = int(random.gauss(base_home, 10))
    away_score = int(random.gauss(base_away, 10))

    if home_score == away_score:
        home_score += 1

    winner = home_team if home_score > away_score else away_team
    return home_score, away_score, winner


class HomeView(TemplateView):
    """
    Display the home page for the NBA fantasy team builder application.

    This page provides a brief description of the project and links to
    players, fantasy teams, and matchups.
    """
    template_name = "project/home.html"


class PlayerListView(ListView):
    """
    Display a list of players with optional filtering and search.

    Supports filtering by position and era, and a case-insensitive search
    on primary_team via query parameters:
        - position
        - era
        - team_name
    """
    model = Player
    template_name = "project/player_list.html"
    context_object_name = "players"
    paginate_by = 10 

    def get_queryset(self):
        """
        Return the filtered queryset of players based on GET parameters.
        """
        qs = Player.objects.all().order_by("last_name", "first_name")
        position = self.request.GET.get("position")
        era = self.request.GET.get("era")
        team_name = self.request.GET.get("team_name")
        player_name = self.request.GET.get("player_name")  

        if position:
            qs = qs.filter(position=position)
        if era:
            qs = qs.filter(era=era)
        if team_name:
            qs = qs.filter(primary_team__icontains=team_name)
        if player_name:
            qs = qs.filter(
                Q(first_name__icontains=player_name)
                | Q(last_name__icontains=player_name)
            )

        return qs

    def get_context_data(self, **kwargs):
        """
        Add the PlayerFilterForm and current query string (without 'page')
        so pagination links preserve the active filters.
        """
        context = super().get_context_data(**kwargs)
        context["filter_form"] = PlayerFilterForm(self.request.GET or None)

        querydict = self.request.GET.copy()
        if "page" in querydict:
            querydict.pop("page")
        context["current_query"] = querydict.urlencode()  # NEW

        return context

class PlayerDetailView(DetailView):
    """
    Display detailed information for a single Player.

    Shows name, position, era, primary team, overall rating, and image
    if available.
    """
    model = Player
    template_name = "project/player_detail.html"
    context_object_name = "player"
class PlayerCreateView(CreateView):
    """
    Allow the user to create a new Player.

    The form includes basic identity info, position, primary team, era,
    overall rating, active status, and an optional image.
    """
    model = Player
    fields = [
        "first_name",
        "last_name",
        "position",
        "primary_team",
        "era",
        "overall_rating",
        "is_active",
        "image",
    ]
    template_name = "project/player_form.html"

    def get_success_url(self):
        """
        After creating a player, redirect to that player's detail page.
        """
        return reverse("player_detail", args=[self.object.pk])


class PlayerUpdateView(UpdateView):
    """
    Allow the user to edit an existing Player.

    Uses the same fields and template as the create view.
    """
    model = Player
    fields = [
        "first_name",
        "last_name",
        "position",
        "primary_team",
        "era",
        "overall_rating",
        "is_active",
        "image",
    ]
    template_name = "project/player_form.html"

    def get_success_url(self):
        """
        After updating a player, redirect back to that player's detail page.
        """
        return reverse("player_detail", args=[self.object.pk])


class PlayerDeleteView(DeleteView):
    """
    Confirm and delete an existing Player.

    After deletion, redirect back to the player list page.
    """
    model = Player
    template_name = "project/player_confirm_delete.html"

    def get_success_url(self):
        """
        After deleting a player, redirect to the player list.
        """
        return reverse("player_list")


class FantasyTeamListView(ListView):
    """
    Display a list of all fantasy teams.

    Each team entry links to the team detail view.
    """
    model = FantasyTeam
    template_name = "project/team_list.html"
    context_object_name = "teams"


class FantasyTeamDetailView(DetailView):
    """
    Display details for a single fantasy team and its roster.

    The view shows the team name, owner, description, and a list of
    TeamMemberships (players on the roster), with links to remove players
    or add new ones.
    """
    model = FantasyTeam
    template_name = "project/team_detail.html"
    context_object_name = "team"


class MatchupListView(ListView):
    """
    Display a list of all matchups.

    Each matchup represents a series between two fantasy teams and links
    to a detail page where the user can simulate games or a full series.
    """
    model = Matchup
    template_name = "project/matchup_list.html"
    context_object_name = "matchups"


class MatchupDetailView(DetailView):
    """
    Display detailed information about a single matchup.

    Shows the home and away teams, status, scheduled date, and any
    simulated score and winner, along with links to simulate again
    or simulate a full best-of-7 series.
    """
    model = Matchup
    template_name = "project/matchup_detail.html"
    context_object_name = "matchup"


class MatchupCreateView(CreateView):
    """
    Allow the user to create a new matchup between two fantasy teams.

    Uses MatchupForm to select home and away teams, series name, and
    optional scheduled date.
    """
    model = Matchup
    form_class = MatchupForm
    template_name = "project/matchup_form.html"

    def get_success_url(self):
        """
        After creating a matchup, redirect to its detail page.
        """
        return reverse("matchup_detail", args=[self.object.pk])


class MatchupUpdateView(UpdateView):
    """
    Allow the user to edit an existing matchup.

    Uses MatchupForm for editing series metadata and participating teams.
    """
    model = Matchup
    form_class = MatchupForm
    template_name = "project/matchup_form.html"

    def get_success_url(self):
        """
        After updating a matchup, redirect back to its detail page.
        """
        return reverse("matchup_detail", args=[self.object.pk])


class MatchupDeleteView(DeleteView):
    """
    Confirm and delete an existing matchup.

    After deletion, the user is returned to the matchup list.
    """
    model = Matchup
    template_name = "project/matchup_confirm_delete.html"

    def get_success_url(self):
        """
        After deleting a matchup, redirect to the matchup list page.
        """
        return reverse("matchup_list")


def simulate_matchup(request, pk):
    """
    Simulate a single game for the given matchup and persist its result.

    Looks up the Matchup by primary key, calls _simulate_single_game to
    generate home and away scores and the winner, stores the result in
    the Matchup (home_score, away_score, status, winner), and then
    redirects back to the matchup detail page.
    """
    matchup = get_object_or_404(Matchup, pk=pk)

    home_team = matchup.home_team
    away_team = matchup.away_team

    home_score, away_score, winner = _simulate_single_game(home_team, away_team)

    matchup.home_score = home_score
    matchup.away_score = away_score
    matchup.status = "simulated"
    matchup.winner = winner
    matchup.save()

    return redirect("matchup_detail", pk=matchup.pk)


def simulate_series(request, pk):
    """
    Simulate a best-of-7 series for the given matchup and render a summary.

    Repeatedly calls _simulate_single_game up to 7 times, stopping early
    when either team reaches 4 wins. Collects all game scores and the
    running win totals, then renders the 'matchup_series_result.html'
    template with a game-by-game breakdown and the final series winner.
    """
    matchup = get_object_or_404(Matchup, pk=pk)
    home_team = matchup.home_team
    away_team = matchup.away_team

    home_wins = 0
    away_wins = 0
    games = []

    for game_number in range(1, 8):  # max 7 games
        home_score, away_score, winner = _simulate_single_game(home_team, away_team)

        if winner == home_team:
            home_wins += 1
        else:
            away_wins += 1

        games.append({
            "number": game_number,
            "home_score": home_score,
            "away_score": away_score,
            "winner": winner,
        })

        if home_wins == 4 or away_wins == 4:
            break

    series_winner = home_team if home_wins > away_wins else away_team

    context = {
        "matchup": matchup,
        "home_team": home_team,
        "away_team": away_team,
        "games": games,
        "home_wins": home_wins,
        "away_wins": away_wins,
        "series_winner": series_winner,
    }
    return render(request, "project/matchup_series_result.html", context)


class FantasyTeamCreateView(CreateView):
    """
    Allow the user to create a new fantasy team.

    The form includes the team name, owner name, and an optional description.
    After creation, the user is redirected to the new team's detail page.
    """
    model = FantasyTeam
    fields = ["name", "owner_name", "description"]
    template_name = "project/team_form.html"

    def get_success_url(self):
        """
        After creating a team, redirect to that team's detail page.
        """
        return reverse("team_detail", args=[self.object.pk])


class FantasyTeamUpdateView(UpdateView):
    """
    Allow the user to edit an existing fantasy team.

    The user can update the team name, owner name, and description.
    """
    model = FantasyTeam
    fields = ["name", "owner_name", "description"]
    template_name = "project/team_form.html"

    def get_success_url(self):
        """
        After updating a team, redirect back to its detail page.
        """
        return reverse("team_detail", args=[self.object.pk])


class FantasyTeamDeleteView(DeleteView):
    """
    Confirm and delete an existing fantasy team.

    After deletion, the user is redirected to the list of all fantasy teams.
    """
    model = FantasyTeam
    template_name = "project/team_confirm_delete.html"

    def get_success_url(self):
        """
        After deleting a team, redirect to the team list page.
        """
        return reverse("team_list")


class TeamMembershipCreateView(CreateView):
    """
    Allow the user to add a new player to a fantasy team's roster.

    The form uses TeamMembershipForm, which filters out players already on
    the team and can optionally filter by a search query (player_query).
    The created TeamMembership links a Player to a FantasyTeam with a role
    and optional jersey number.
    """
    model = TeamMembership
    form_class = TeamMembershipForm
    template_name = "project/team_add_player.html"

    def get_team(self):
        """
        Helper to retrieve the FantasyTeam being modified based on the URL.
        """
        return FantasyTeam.objects.get(pk=self.kwargs["team_id"])

    def get_form_kwargs(self):
        """
        Pass the current team and optional player search query into the form.

        This allows the form to restrict available players to those not already
        on the team and optionally filter them based on player_query.
        """
        kwargs = super().get_form_kwargs()
        team = self.get_team()
        player_query = self.request.GET.get("player_query", "")

        kwargs["team"] = team
        kwargs["player_query"] = player_query
        return kwargs

    def form_valid(self, form):
        """
        Before saving, associate the new TeamMembership with the correct team.
        """
        form.instance.team = self.get_team()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Add the current team and the active player_query to the template context.
        """
        context = super().get_context_data(**kwargs)
        context["team"] = self.get_team()
        context["player_query"] = self.request.GET.get("player_query", "")
        return context

    def get_success_url(self):
        """
        After adding a player, redirect back to that team's detail page.
        """
        return reverse("team_detail", args=[self.kwargs["team_id"]])


class TeamMembershipDeleteView(DeleteView):
    """
    Confirm and remove a player from a fantasy team's roster.

    Deletes a single TeamMembership instance and then redirects back to
    the associated team's detail page.
    """
    model = TeamMembership
    template_name = "project/membership_confirm_delete.html"

    def get_success_url(self):
        """
        After removing the player from the team, redirect to that team's detail.
        """
        team_id = self.object.team.pk
        return reverse("team_detail", args=[team_id])

