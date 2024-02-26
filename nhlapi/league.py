from datetime import date

import requests


def get_franchises():
    resp = requests.get("https://api.nhle.com/stats/rest/en/franchise")

    return resp.json()
