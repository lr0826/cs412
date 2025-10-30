from django.db import models
from datetime import datetime

from django.utils import timezone
# Create your models here.
class Voter(models.Model):
    ''' data model that represents a registered voter '''
    voter_id = models.TextField(blank=True)
    last_name = models.TextField()
    first_name = models.TextField()
    residential_street_number = models.TextField()
    residential_street_name = models.TextField()
    residential_apartment_number = models.TextField()
    residential_zipcode = models.IntegerField()
    date_of_birth = models.DateTimeField(null=True)
    date_of_registration = models.DateTimeField(null=True)
    party_affiliation = models.CharField(max_length=2)
    precinct_number = models.TextField()
    voter_score = models.IntegerField()
    v20state = models.BooleanField()
    v21town = models.BooleanField()
    v21primary = models.BooleanField()
    v22general = models.BooleanField()
    v23town = models.BooleanField()
    def __str__(self):
        ''' Return a string representation of this model instance '''
        return f'{self.first_name} {self.last_name}'


def load_data():
    ''' Function to load data records from csv file into the Django Database '''
    Voter.objects.all().delete()
    filename = '/Users/liurun0826/Desktop/newton_voters.csv'
    f = open(filename, 'r')

    # throw away header row
    f.readline()

    for line in f:

        # split by comma
        fields = line.strip().split(',')

        # columns we assume:
        # 0 voter_id
        # 1 last_name
        # 2 first_name
        # 3 Residential Address - Street Number
        # 4 Residential Address - Street Name
        # 5 Residential Address - Apartment Number
        # 6 Residential Address - Zip Code
        # 7 Date of Birth                 e.g. 1980-01-03
        # 8 Date of Registration          e.g. 2022-11-26
        # 9 Party Affiliation             e.g. "U", "D"
        # 10 Precinct Number              e.g. 1
        # 11 v20state                     e.g. TRUE / FALSE
        # 12 v21town
        # 13 v21primary
        # 14 v22general
        # 15 v23town                      
        # 16 voter_score

        # helpers ---------------------------------
        def _strip_quotes(s: str) -> str:
            s = (s or "").strip()
            if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
                return s[1:-1].strip()
            return s
        def parse_datetime_yyyy_mm_dd(s):
            """
            Return timezone-aware datetime if s is a valid 'YYYY-MM-DD'.
            Return None if s is empty or invalid.
            """
            s = _strip_quotes(s)
            if not s:
                return None
            try:
                dt = datetime.strptime(s, "%Y-%m-%d")
                # make timezone-aware to avoid Django warning
                return timezone.make_aware(dt)
            except ValueError:
                # bad date -> store NULL rather than a fake date
                return None

        def parse_bool(s):
            s = s.strip().upper()
            return s == "TRUE"

        def parse_int(s):
            s = s.strip()
            if s == "":
                return 0
            return int(s)

        # build and save model instance ------------
        result = Voter(
            voter_id = fields[0].strip(),

            last_name = fields[1].strip(),
            first_name = fields[2].strip(),

            residential_street_number = fields[3].strip(),
            residential_street_name = fields[4].strip(),
            residential_apartment_number = fields[5].strip(),
            residential_zipcode = parse_int(fields[6]),

            date_of_birth = parse_datetime_yyyy_mm_dd(fields[7]),
            date_of_registration = parse_datetime_yyyy_mm_dd(fields[8]),

            party_affiliation = fields[9].strip(),
            precinct_number = fields[10].strip(),

            v20state = parse_bool(fields[11]),
            v21town = parse_bool(fields[12]),
            v21primary = parse_bool(fields[13]),
            v22general = parse_bool(fields[14]),
            v23town = parse_bool(fields[15]),

            voter_score = parse_int(fields[16]),
        )

        result.save()
    
    f.close()
    return "done"
