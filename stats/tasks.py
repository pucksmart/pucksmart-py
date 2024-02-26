from datetime import date

from celery import shared_task

import nhlapi.schedule
import nhlapi.league
from stats.models import Franchise


@shared_task
def load_franchises():
    franchises = nhlapi.league.get_franchises()
    for f in franchises['data']:
        franchise = Franchise()
        franchise.id = f['id']
    print(franchises)
    return franchises


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
