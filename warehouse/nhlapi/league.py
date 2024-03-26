import requests


def get_franchises():
    return requests.get("https://api.nhle.com/stats/rest/en/franchise")


def get_teams():
    return requests.get("https://api.nhle.com/stats/rest/en/team")


def get_seasons():
    return requests.get("https://api.nhle.com/stats/rest/en/season")
