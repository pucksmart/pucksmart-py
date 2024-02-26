# GET https://api-web.nhle.com/v1/schedule/2023-09-23
# GET https://api-web.nhle.com/v1/schedule/now
from datetime import date, datetime

import requests


def get_week_schedule(start_day: date = date.today()):
    resp = requests.get("https://api-web.nhle.com/v1/schedule/" + start_day.isoformat())

    return resp.json()
