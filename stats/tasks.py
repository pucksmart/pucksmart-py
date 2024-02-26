from datetime import date

from celery import shared_task

import nhlapi.schedule


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
