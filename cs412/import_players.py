import csv
from pathlib import Path

from django.db import transaction
from project.models import Player

# Base directory = folder where manage.py and this script live
BASE_DIR = Path(__file__).resolve().parent
csv_path = BASE_DIR / "project" / "data" / "nba2k20-full.csv"


def map_position(raw):
    """
    Map NBA 2K position codes like 'G', 'F', 'C-F', 'G-F' etc.
    to one of: PG, SG, SF, PF, C.
    """
    raw = (raw or "").upper()

    if "C" in raw:
        return "C"
    if "G" in raw:
        # We'll just call all guards PG for this project
        return "PG"
    if "F" in raw:
        # Treat forwards as SF
        return "SF"

    # Fallback
    return "SF"


@transaction.atomic
def import_players():
    if not csv_path.exists():
        print(f"CSV file not found at: {csv_path}")
        return

    created_count = 0
    skipped_count = 0

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            full_name = (row.get("full_name") or "").strip()
            if not full_name:
                skipped_count += 1
                continue

            parts = full_name.split()
            first_name = parts[0]
            last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

            rating_str = row.get("rating") or "0"
            try:
                overall_rating = int(float(rating_str))
            except ValueError:
                overall_rating = 0

            team_raw = (row.get("team") or "").strip()
            pos_raw = (row.get("position") or "").strip()

            position = map_position(pos_raw)

            # Treat everyone in this 2K20 file as "2020s/Current"
            era = "20s"

            player, created = Player.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                primary_team=team_raw,
                defaults={
                    "position": position,
                    "era": era,
                    "overall_rating": overall_rating,
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
            else:
                skipped_count += 1

    print(
        f"Import complete. Created {created_count} players, "
        f"skipped {skipped_count} existing."
    )


# actually run it when this script is executed
import_players()
