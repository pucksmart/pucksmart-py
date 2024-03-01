import zoneinfo
from datetime import date, datetime, timezone

from celery import shared_task

import nhlapi.schedule
import nhlapi.league
from stats.models import Franchise, Team, Season


def eastern_datetime(value: str) -> datetime:
    return datetime(value, tzinfo=zoneinfo.ZoneInfo('America/New_York')).astimezone(tz=timezone.utc)


@shared_task
def load_franchises():
    franchises_resp = nhlapi.league.get_franchises()
    franchises = []
    for f in franchises_resp['data']:
        franchise = Franchise()
        franchise.id = f['id']
        franchise.full_name = f['fullName']
        franchise.common_name = f['teamCommonName']
        franchise.place_name = f['teamPlaceName']
        franchises.append(franchise)
    Franchise.objects.bulk_create(franchises, ignore_conflicts=True)

    print(franchises)


@shared_task
def load_teams():
    teams_resp = nhlapi.league.get_teams()
    teams = []
    for t in teams_resp['data']:
        team = Team()
        team.id = t['id']
        team.name = t['fullName']
        team.abbreviation = t['rawTricode']
        if t['franchiseId']:
            team.franchise = Franchise.objects.get(id=t['franchiseId'])
        teams.append(team)
    Team.objects.bulk_create(teams, ignore_conflicts=True)

    print(teams)


@shared_task
def load_seasons():
    seasons_resp = nhlapi.league.get_seasons()
    seasons = []
    for s in seasons_resp['data']:
        season = Season()
        season.id = s['id']
        season.formatted_season_id = s['formattedSeasonId']
        season.start_date = eastern_datetime(s['startDate'])
        season.end_date = eastern_datetime(s['endDate'])
        season.preseason_start_date = eastern_datetime(s['preseasonStartdate'])
        season.regular_season_end_date = eastern_datetime(s['regularSeasonEndDate'])
        seasons.append(season)
    Season.objects.bulk_create(seasons, ignore_conflicts=True)

    print(seasons)


@shared_task
def scan_games_today():
    schedule = nhlapi.schedule.get_week_schedule(date.today())
    print(schedule)
    return schedule


@shared_task
def back_fill_games(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)
