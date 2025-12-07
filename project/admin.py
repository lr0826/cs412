from django.contrib import admin
from .models import Player, FantasyTeam, TeamMembership, Matchup

# Register your models here.
admin.site.register(Player)
admin.site.register(FantasyTeam)
admin.site.register(TeamMembership)
admin.site.register(Matchup)
