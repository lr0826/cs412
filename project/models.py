# File: models.py
# Author: Run Liu (lr0826@bu.edu), 11/20/2025
# Description: The models python file for the nba fantasy team final project

from django.db import models


class Player(models.Model):
    """
    Represent a real-life NBA player that can be drafted onto fantasy teams.

    This model stores basic identity information (first and last name),
    their primary position, the main real-life franchise they are associated
    with, an era label, and a 1–100 overall rating. Players can be active or
    retired, and may optionally have an image uploaded.

    A Player can appear on multiple FantasyTeam rosters through TeamMembership.
    """

    POSITION_CHOICES = [
        ("PG", "Point Guard"),
        ("SG", "Shooting Guard"),
        ("SF", "Small Forward"),
        ("PF", "Power Forward"),
        ("C", "Center"),
    ]

    ERA_CHOICES = [
        ("60s", "1960s"),
        ("70s", "1970s"),
        ("80s", "1980s"),
        ("90s", "1990s"),
        ("00s", "2000s"),
        ("10s", "2010s"),
        ("20s", "2020s/Current"),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=2, choices=POSITION_CHOICES)
    primary_team = models.CharField(max_length=50)  # e.g., "Los Angeles Lakers"
    era = models.CharField(max_length=3, choices=ERA_CHOICES)
    overall_rating = models.PositiveIntegerField()  # e.g., 1–100 (used in simulation)
    is_active = models.BooleanField(default=False)
    image = models.ImageField(upload_to="player_images/", blank=True, null=True)

    def __str__(self):
        """
        Return a short human-readable label for the player.
        """
        return f"{self.first_name} {self.last_name} ({self.position})"


class FantasyTeam(models.Model):
    """
    Represent a user-created fantasy team composed of NBA players.

    A FantasyTeam has a name, an owner name (not tied to Django auth users
    for simplicity), an optional description, and a timestamp indicating when
    it was created. The roster for a team is defined via TeamMembership
    records that link Players to this FantasyTeam.
    """

    name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Return the fantasy team's name as its label.
        """
        return self.name


class TeamMembership(models.Model):
    """
    Link a Player to a FantasyTeam as part of that team's roster.

    Each TeamMembership represents a single player on a specific fantasy team,
    with a role (starter or bench), an optional jersey number, and the time
    when they were added. The (team, player) pair is constrained to be unique
    so that the same player cannot be added to the same fantasy team twice.
    """

    ROLE_CHOICES = [
        ("starter", "Starter"),
        ("bench", "Bench"),
    ]

    team = models.ForeignKey(
        FantasyTeam,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="starter")
    jersey_number = models.PositiveIntegerField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Meta configuration to prevent duplicate roster entries.

        The unique_together constraint enforces that a given player can only
        appear once on a specific fantasy team.
        """
        unique_together = ("team", "player")

    def __str__(self):
        """
        Return a readable label describing the player's membership on a team.
        """
        return f"{self.player} on {self.team} ({self.role})"


class Matchup(models.Model):
    """
    Represent a series or game between two fantasy teams.

    A Matchup stores the home and away teams, an optional series name
    (e.g., "Finals"), a game number label, and an optional scheduled date.
    When a simulation is run, the model can store the resulting home and
    away scores, the winning team, and a status flag describing whether
    the matchup has been scheduled, simulated, or completed.

    Multiple Matchup instances can be used together to model tournaments
    or multi-round series.
    """

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("simulated", "Simulated"),
        ("completed", "Completed"),
    ]

    home_team = models.ForeignKey(
        FantasyTeam,
        on_delete=models.CASCADE,
        related_name="home_matchups",
    )
    away_team = models.ForeignKey(
        FantasyTeam,
        on_delete=models.CASCADE,
        related_name="away_matchups",
    )
    series_name = models.CharField(max_length=100, blank=True)
    game_number = models.PositiveIntegerField(default=1)
    scheduled_date = models.DateField(blank=True, null=True)

    home_score = models.IntegerField(blank=True, null=True)
    away_score = models.IntegerField(blank=True, null=True)

    winner = models.ForeignKey(
        FantasyTeam,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="won_matchups",
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="scheduled",
    )

    def __str__(self):
        """
        Return a descriptive label including the teams and game number.
        """
        return (
            f"{self.series_name or 'Matchup'}: "
            f"{self.home_team} vs {self.away_team} (Game {self.game_number})"
        )


