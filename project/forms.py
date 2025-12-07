# File: forms.py
# Author: Run Liu (lr0826@bu.edu), 11/29/2025
# Description: Forms for NBA fantasy team project

from django import forms
from .models import *
from django.db.models import Q


class TeamMembershipForm(forms.ModelForm):
    """
    Form for adding a Player to a FantasyTeam's roster.

    This form is backed by the TeamMembership model and expects a 'team'
    keyword argument in its constructor. It filters the Player queryset so
    that:
        - players already on the team are excluded, and
        - an optional search query (player_query) can be used to narrow down
          players by first name, last name, or primary team.
    """
    class Meta:
        model = TeamMembership
        fields = ["player", "role", "jersey_number"]

    def __init__(self, *args, **kwargs):
        """
        Customize the form's player field queryset based on the team and
        optional player search query.

        Parameters (via kwargs):
            team: FantasyTeam instance or None
            player_query: search string to filter players by name or team
        """
        team: FantasyTeam | None = kwargs.pop("team", None)
        player_query: str = kwargs.pop("player_query", "")
        super().__init__(*args, **kwargs)

        qs = Player.objects.all().order_by("last_name", "first_name")

        # Filter out players already on this team
        if team is not None:
            existing_ids = team.memberships.values_list("player_id", flat=True)
            qs = qs.exclude(id__in=existing_ids)

        # Apply search filter if provided
        if player_query:
            qs = qs.filter(
                Q(first_name__icontains=player_query)
                | Q(last_name__icontains=player_query)
                | Q(primary_team__icontains=player_query)
            )

        self.fields["player"].queryset = qs


class MatchupForm(forms.ModelForm):
    """
    Form for creating or editing a Matchup between two fantasy teams.

    The form allows the user to choose a home team, an away team, an optional
    series name, and a scheduled date. It enforces that the home and away
    teams must be different.
    """
    class Meta:
        model = Matchup
        fields = [
            "series_name",
            "home_team",
            "away_team",
            "scheduled_date",
        ]

    def __init__(self, *args, **kwargs):
        """
        Order the home_team and away_team dropdowns alphabetically by team name.
        """
        super().__init__(*args, **kwargs)
        self.fields["home_team"].queryset = FantasyTeam.objects.order_by("name")
        self.fields["away_team"].queryset = FantasyTeam.objects.order_by("name")

    def clean(self):
        """
        Validate that the selected home and away teams are not the same.

        If both teams are provided and they are equal, raise a ValidationError.
        """
        cleaned_data = super().clean()
        home = cleaned_data.get("home_team")
        away = cleaned_data.get("away_team")

        if home and away and home == away:
            raise forms.ValidationError("Home team and away team must be different.")

        return cleaned_data


class PlayerFilterForm(forms.Form):
    """
    Simple filter/search form for narrowing down the list of players.

    This form is used on the player list page to support:
        - filtering by position (or any position),
        - filtering by era (or any era),
        - searching by real-life team name (case-insensitive substring), and
        - searching by player name, matching either first or last name.
    """
    position = forms.ChoiceField(
        choices=[("", "Any position")] + list(Player.POSITION_CHOICES),
        required=False,
        label="Position",
    )
    era = forms.ChoiceField(
        choices=[("", "Any era")] + list(Player.ERA_CHOICES),
        required=False,
        label="Era",
    )
    team_name = forms.CharField(
        required=False,
        label="Real-life team contains",
    )
    player_name = forms.CharField(
        required=False,
        label="Player name contains",
    )
