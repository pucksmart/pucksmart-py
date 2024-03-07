import requests


def get_game_play_by_play(game_id: str):
    resp = requests.get("https://api-web.nhle.com/v1/gamecenter/%s/play-by-play" % game_id)
    return resp.json()


def get_game_shifts(game_id: str):
    resp = requests.get("https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId=%s" % game_id)
    return resp.json()
