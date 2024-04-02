from datetime import datetime, timedelta, timezone
from io import StringIO
from itertools import product
from string import ascii_lowercase

import boto3
import pandas as pd
import requests
from botocore.config import Config
from celery import shared_task

from stats.models import Game
from warehouse.models import HttpSource, NhlPlayer

s3 = boto3.resource(
    "s3",
    endpoint_url="http://localhost:9000",
    config=Config(signature_version="s3v4"),
    aws_access_key_id="accesskey",
    aws_secret_access_key="secretkey",
    aws_session_token=None,
    verify=False,
)


@shared_task
def load_play_by_play(game_id: int):
    url = "https://api-web.nhle.com/v1/gamecenter/%d/play-by-play" % game_id
    try:
        source = HttpSource.objects.get(url=url)
    except HttpSource.DoesNotExist:
        source = HttpSource(url=url)

    if not source.last_refreshed or source.last_refreshed + timedelta(
        days=1
    ) < datetime.now(timezone.utc):
        e_tag = ""
        if source.e_tag:
            r = requests.head(source.url, allow_redirects=True)
            e_tag = r.headers.get("ETag")
        if not source.e_tag or e_tag != source.e_tag:
            r = requests.get(source.url, allow_redirects=True)
            source.e_tag = r.headers.get("ETag")
            source.last_refreshed = datetime.now(timezone.utc)
            source.blob_path = "source/game/%d/play-by-play" % game_id
            s3.Object("pucksmart", source.blob_path).put(Body=r.content)
    source.save()


@shared_task
def load_shifts(game_id: int):
    url = (
        "https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId=%d" % game_id
    )
    try:
        source = HttpSource.objects.get(url=url)
    except HttpSource.DoesNotExist:
        source = HttpSource(url=url)

    if not source.last_refreshed or source.last_refreshed + timedelta(
        days=1
    ) < datetime.now(timezone.utc):
        e_tag = ""
        if source.e_tag:
            r = requests.head(source.url, allow_redirects=True)
            e_tag = r.headers.get("ETag")
        if not source.e_tag or e_tag != source.e_tag:
            r = requests.get(source.url, allow_redirects=True)
            source.e_tag = r.headers.get("ETag")
            source.last_refreshed = datetime.now(timezone.utc)
            source.blob_path = "source/game/%d/shifts" % game_id
            s3.Object("pucksmart", source.blob_path).put(Body=r.content)
    source.save()


def _get_player_ids_from_boxscore(boxscore):
    player_ids = []
    for p in boxscore["playerByGameStats"]["awayTeam"]["forwards"]:
        player_ids.append(p["playerId"])
    for p in boxscore["playerByGameStats"]["awayTeam"]["defense"]:
        player_ids.append(p["playerId"])
    for p in boxscore["playerByGameStats"]["awayTeam"]["goalies"]:
        player_ids.append(p["playerId"])
    for p in boxscore["summary"]["gameInfo"]["awayTeam"]["scratches"]:
        player_ids.append(p["id"])
    for p in boxscore["playerByGameStats"]["homeTeam"]["forwards"]:
        player_ids.append(p["playerId"])
    for p in boxscore["playerByGameStats"]["homeTeam"]["defense"]:
        player_ids.append(p["playerId"])
    for p in boxscore["playerByGameStats"]["homeTeam"]["goalies"]:
        player_ids.append(p["playerId"])
    for p in boxscore["summary"]["gameInfo"]["homeTeam"]["scratches"]:
        player_ids.append(p["id"])
    return player_ids


@shared_task
def load_boxscore(game_id: int):
    url = "https://api-web.nhle.com/v1/gamecenter/%d/boxscore" % game_id
    try:
        source = HttpSource.objects.get(url=url)
    except HttpSource.DoesNotExist:
        source = HttpSource(url=url)

    if not source.last_refreshed or source.last_refreshed + timedelta(
        days=1
    ) < datetime.now(timezone.utc):
        e_tag = ""
        if source.e_tag:
            r = requests.head(source.url, allow_redirects=True)
            e_tag = r.headers.get("ETag")
        if not source.e_tag or e_tag != source.e_tag:
            r = requests.get(source.url, allow_redirects=True)
            source.e_tag = r.headers.get("ETag")
            source.last_refreshed = datetime.now(timezone.utc)
            source.blob_path = "source/game/%d/boxscore" % game_id
            s3.Object("pucksmart", source.blob_path).put(Body=r.content)

            players = _get_player_ids_from_boxscore(r.json())
            load_player.map(players).apply_async()
    source.save()


@shared_task
def load_player(nhl_id: int):
    url = "https://api-web.nhle.com/v1/player/%d/landing" % nhl_id
    try:
        player = NhlPlayer.objects.get(nhl_id=nhl_id)
    except NhlPlayer.DoesNotExist:
        player = NhlPlayer(nhl_id=nhl_id)

    player_summary = requests.get(url, allow_redirects=True).json()
    player.given_name = player_summary["firstName"]["default"]
    player.family_name = player_summary["lastName"]["default"]
    player.is_active = player_summary["isActive"]
    player.position = player_summary["position"]
    player.hall_of_fame = player_summary["inHHOF"]
    player.birth_date = player_summary["birthDate"]
    player.birth_locality = player_summary["birthCity"]["default"]
    if "birthStateProvince" in player_summary:
        player.birth_region = player_summary["birthStateProvince"]["default"]
    player.birth_country = player_summary["birthCountry"]
    if "shootsCatches" in player_summary:
        player.handedness = player_summary["shootsCatches"]
    if "heightInCentimeters" in player_summary:
        player.height = player_summary["heightInCentimeters"]
    if "weightInKilograms" in player_summary:
        player.weight = player_summary["weightInKilograms"]

    player.save()


@shared_task
def backfill_game_reports():
    for g in Game.objects.all():
        load_boxscore.s(g.id).apply_async()
        load_play_by_play.s(g.id).apply_async()
        load_shifts.s(g.id).apply_async()


@shared_task
def load_players():
    search_terms = map("".join, product(ascii_lowercase, repeat=3))
    players = []
    for search_term in search_terms:
        url = (
            "https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit=1000&q="
            + search_term
        )
        r = requests.get(url)
        print(search_term)
        players = players + r.json()
        print(len(players))
    df = pd.DataFrame(players)
    print(df.shape)

    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    s3.Object("pucksmart", "source/players.csv").put(Body=csv_buffer.getvalue())
