# File: views.py
# Author: Run Liu (lr0826@bu.edu), 10/28/2025
# Description: The view python file for the voter analytics application
from django.shortcuts import render


from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import *
from django.db.models.functions import ExtractYear, Trim
from django.db.models.functions import TruncYear
from django.db.models import Count
# import plotly library for graphing
import plotly
import plotly.graph_objs as go
from plotly.offline import plot


class VoterListView(ListView):
    model = Voter
    template_name = 'voter_analytics/voter_list.html'
    context_object_name = 'voters'
    paginate_by = 100  # requirement: show 100 at a time
    def get_queryset(self):
        """
        Build a queryset of Voter objects, optionally filtered by:
        - party
        - min_dob_year
        - max_dob_year
        - voter_score
        - voted in specific elections
        """
        qs = Voter.objects.all()

        # pull filter inputs from GET params
        party = self.request.GET.get('party', '').strip()
        min_dob_year = self.request.GET.get('min_dob_year', '').strip()
        max_dob_year = self.request.GET.get('max_dob_year', '').strip()
        voter_score = self.request.GET.get('voter_score', '').strip()

        # checkboxes for past elections
        voted_v20state = self.request.GET.get('v20state', '')
        voted_v21town = self.request.GET.get('v21town', '')
        voted_v21primary = self.request.GET.get('v21primary', '')
        voted_v22general = self.request.GET.get('v22general', '')
        voted_v23town = self.request.GET.get('v23town', '')

        
        if party != '':
            qs = qs.filter(party_affiliation__iexact=party)

        # date_of_birth is a DateTimeField.
        # We only care about YEAR filtering. We interpret:
        #  - min_dob_year = born >= Jan 1 of that year
        #  - max_dob_year = born <= Dec 31 of that year
        #
        # super important: rows where date_of_birth is NULL shouldn't kill the filter logic.
        if min_dob_year != '':
            # born on or after Jan 1 <year> 00:00
            qs = qs.filter(date_of_birth__year__gte=int(min_dob_year))

        if max_dob_year != '':
            # born on or before Dec 31 <year> 23:59, so just <= that year
            qs = qs.filter(date_of_birth__year__lte=int(max_dob_year))

        # voter score
        if voter_score != '':
            qs = qs.filter(voter_score=int(voter_score))

        # elections checkboxes
        # If a box is checked, the GET param exists. If not checked, it's missing.
        if voted_v20state:
            qs = qs.filter(v20state=True)
        if voted_v21town:
            qs = qs.filter(v21town=True)
        if voted_v21primary:
            qs = qs.filter(v21primary=True)
        if voted_v22general:
            qs = qs.filter(v22general=True)
        if voted_v23town:
            qs = qs.filter(v23town=True)

        # default sort (optional): maybe show most reliable (high score) first
        qs = qs.order_by('-voter_score', 'last_name', 'first_name')

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Party dropdown options
        party_values = (
            Voter.objects
            .exclude(party_affiliation__isnull=True)
            .exclude(party_affiliation__exact='')
            .values_list('party_affiliation', flat=True)
            .distinct()
        )
        normalized_party_values = sorted({p.strip() for p in party_values})

        # Birth year dropdown options
        # Step 1: get distinct datetimes truncated to year from date_of_birth
        dob_year_datetimes = (
            Voter.objects
            .exclude(date_of_birth__isnull=True)
            .datetimes('date_of_birth', 'year')  # returns datetimes like 1947-01-01 00:00, 1995-01-01 00:00, ...
        )
        # Step 2: pull just the .year from those datetimes
        dob_year_options = sorted({dt.year for dt in dob_year_datetimes})

        # Voter score options
        score_values = (
            Voter.objects
            .exclude(voter_score__isnull=True)
            .values_list('voter_score', flat=True)
            .distinct()
        )
        score_options = sorted(score_values)

        request = self.request
        ctx['filter_party'] = request.GET.get('party', '').strip()
        ctx['filter_min_dob_year'] = request.GET.get('min_dob_year', '').strip()
        ctx['filter_max_dob_year'] = request.GET.get('max_dob_year', '').strip()
        ctx['filter_voter_score'] = request.GET.get('voter_score', '').strip()

        ctx['filter_v20state'] = 'checked' if request.GET.get('v20state', '') else ''
        ctx['filter_v21town'] = 'checked' if request.GET.get('v21town', '') else ''
        ctx['filter_v21primary'] = 'checked' if request.GET.get('v21primary', '') else ''
        ctx['filter_v22general'] = 'checked' if request.GET.get('v22general', '') else ''
        ctx['filter_v23town'] = 'checked' if request.GET.get('v23town', '') else ''

        ctx['party_options'] = normalized_party_values
        ctx['dob_year_options'] = dob_year_options
        ctx['score_options'] = score_options
        # -------- build querystring WITHOUT page=
        # so pagination links don't duplicate ?page
        params = request.GET.copy()
        if 'page' in params:
            del params['page']
        # urlencode() makes "party=D&min_dob_year=1970&..."
        ctx['querystring_without_page'] = params.urlencode()
        params = request.GET.copy()
        if 'page' in params:
            del params['page']
        # urlencode() makes "party=D&min_dob_year=1970&..."
        ctx['querystring_without_page'] = params.urlencode()
        return ctx


class VoterDetailView(DetailView):
    ''' detail view page for one specific voter '''
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'
class GraphListView(ListView):
    model = Voter
    template_name = 'voter_analytics/graphs.html'
    context_object_name = 'voters'   
    paginate_by = None #no pagination needed
    ''' List View to display multiple graphs for a set of voters '''
    def get_queryset(self):
        ''' filtering out the query set, similar to task 2 '''
        qs = Voter.objects.all()

        rq = self.request
        party = rq.GET.get('party', '').strip()
        min_dob_year = rq.GET.get('min_dob_year', '').strip()
        max_dob_year = rq.GET.get('max_dob_year', '').strip()
        voter_score = rq.GET.get('voter_score', '').strip()

        if party != '':
            qs = qs.filter(party_affiliation__iexact=party)

        if min_dob_year != '':
            qs = qs.filter(date_of_birth__year__gte=int(min_dob_year))
        if max_dob_year != '':
            qs = qs.filter(date_of_birth__year__lte=int(max_dob_year))

        if voter_score != '':
            qs = qs.filter(voter_score=int(voter_score))

        if rq.GET.get('v20state', ''):
            qs = qs.filter(v20state=True)
        if rq.GET.get('v21town', ''):
            qs = qs.filter(v21town=True)
        if rq.GET.get('v21primary', ''):
            qs = qs.filter(v21primary=True)
        if rq.GET.get('v22general', ''):
            qs = qs.filter(v22general=True)
        if rq.GET.get('v23town', ''):
            qs = qs.filter(v23town=True)

        # no particular ordering needed for graphs
        return qs
    def get_context_data(self, **kwargs):
        ''' override the get_context_data method to create the graphs using plotly '''
        ctx = super().get_context_data(**kwargs)
        qs = ctx['voters']  # filtered queryset from get_queryset()

        
        party_values = (
            Voter.objects
            .exclude(party_affiliation__isnull=True)
            .exclude(party_affiliation__exact='')
            .values_list('party_affiliation', flat=True)
            .distinct()
        )
        ctx['party_options'] = sorted({p.strip() for p in party_values})

        dob_year_datetimes = (
            Voter.objects
            .exclude(date_of_birth__isnull=True)
            .datetimes('date_of_birth', 'year')
        )
        ctx['dob_year_options'] = sorted({dt.year for dt in dob_year_datetimes})

        score_values = (
            Voter.objects
            .exclude(voter_score__isnull=True)
            .values_list('voter_score', flat=True)
            .distinct()
        )
        ctx['score_options'] = sorted(score_values)

        
        rq = self.request
        ctx['filter_party'] = rq.GET.get('party', '').strip()
        ctx['filter_min_dob_year'] = rq.GET.get('min_dob_year', '').strip()
        ctx['filter_max_dob_year'] = rq.GET.get('max_dob_year', '').strip()
        ctx['filter_voter_score'] = rq.GET.get('voter_score', '').strip()
        ctx['filter_v20state'] = 'checked' if rq.GET.get('v20state', '') else ''
        ctx['filter_v21town'] = 'checked' if rq.GET.get('v21town', '') else ''
        ctx['filter_v21primary'] = 'checked' if rq.GET.get('v21primary', '') else ''
        ctx['filter_v22general'] = 'checked' if rq.GET.get('v22general', '') else ''
        ctx['filter_v23town'] = 'checked' if rq.GET.get('v23town', '') else ''

        # ------- Chart 1: Birth year histogram ------
        by_year = (
            qs.exclude(date_of_birth__isnull=True)
            .values('date_of_birth__year')                 
            .annotate(count=Count('id'))
            .order_by('date_of_birth__year')
        )

        years  = [row['date_of_birth__year'] for row in by_year if row['date_of_birth__year'] is not None]
        counts = [row['count'] for row in by_year if row['date_of_birth__year'] is not None]

        # If you want years as strings (categorical axis):
        years = list(map(str, years))

        fig_births = go.Figure(data=[go.Bar(x=years, y=counts)])
        fig_births.update_layout(
            title="Voters Distributed by Birth Year",
            xaxis_title="Birth Year",
            yaxis_title="Count",
            margin=dict(l=30, r=10, t=40, b=30),
        )
        # Make sure Plotly JS loads once on the page
        ctx['graph_births'] = plot(fig_births, output_type='div', include_plotlyjs='cdn')



        # ------- Chart 2: Party distribution (pie) -------
        party_rows = (
            qs.annotate(party_norm=Trim('party_affiliation'))
              .values('party_norm')
              .annotate(count=Count('id'))
              .order_by('party_norm')
        )
        party_labels = []
        party_counts = []
        for row in party_rows:
            label = row['party_norm'] if row['party_norm'] not in (None, '') else '(none)'
            party_labels.append(label)
            party_counts.append(row['count'])

        fig_party = go.Figure(data=[go.Pie(labels=party_labels, values=party_counts, hole=0)])
        fig_party.update_layout(
            title="Voters by Party Affiliation",
            margin=dict(l=30, r=10, t=40, b=30),
        )
        ctx['graph_party'] = plot(fig_party, output_type='div', include_plotlyjs=False)

        # ------- Chart 3: Participation counts (bar) -------
        labels = ["2020 State", "2021 Town", "2021 Primary", "2022 General", "2023 Town"]
        values = [
            qs.filter(v20state=True).count(),
            qs.filter(v21town=True).count(),
            qs.filter(v21primary=True).count(),
            qs.filter(v22general=True).count(),
            qs.filter(v23town=True).count(),
        ]

        fig_elections = go.Figure(data=[go.Bar(x=labels, y=values)])
        fig_elections.update_layout(
            title="Participation by Election",
            xaxis_title="Election",
            yaxis_title="Voter Count",
            margin=dict(l=30, r=10, t=40, b=30),
        )
        ctx['graph_elections'] = plot(fig_elections, output_type='div', include_plotlyjs=False)

        return ctx   
        