import requests


shot_type_mapping = {
    505: "GOAL",
    506: "SHOT_ON_GOAL",
    507: "MISSED",
    508: "BLOCKED",
}


def get_game_play_by_play(game_id: int):
    return requests.get("https://api-web.nhle.com/v1/gamecenter/%d/play-by-play" % game_id)


def get_game_shifts(game_id: int):
    return requests.get("https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId=%d" % game_id)
