from datetime import date

from celery import shared_task

import nhlapi.schedule
import nhlapi.league
from stats.models import Franchise, Team


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
    Franchise.objects.bulk_create(franchises)

    print(franchises)
    return franchises


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
    return teams

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
