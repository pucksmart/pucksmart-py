import zoneinfo
from datetime import date, datetime, timezone, timedelta

from celery import chain, group, shared_task

import nhlapi.game
import nhlapi.league
import nhlapi.schedule
from stats.models import Franchise, Season, Team, Game, Shot, Faceoff


def _eastern_iso_to_utc(value: str) -> datetime | None:
    if not value:
        return None
    timestamp = datetime.fromisoformat(value).replace(
        tzinfo=zoneinfo.ZoneInfo(key="America/New_York")
    )
    return timestamp.astimezone(timezone.utc)


def _scoreboard_time_to_seconds(scoreboard_time: str) -> int:
    (minutes, seconds) = tuple(scoreboard_time.split(":"))
    return int(minutes) * 60 + int(seconds)


@shared_task
def preload():
    chain(
        group(
            load_seasons.apply_async(),
            chain(
                load_franchises.signature(args=()),
                load_teams.signature(args=(), immutable=True),
            ).apply_async(),
        ),
        load_games.apply_async()
    )


@shared_task
def load_franchises():
    franchises_resp = nhlapi.league.get_franchises()
    franchises = []
    for f in franchises_resp["data"]:
        franchise = Franchise()
        franchise.id = f["id"]
        franchise.full_name = f["fullName"]
        franchise.common_name = f["teamCommonName"]
        franchise.place_name = f["teamPlaceName"]
        franchises.append(franchise)
    Franchise.objects.bulk_create(franchises, ignore_conflicts=True)

    print(franchises)


@shared_task
def load_teams():
    teams_resp = nhlapi.league.get_teams()
    teams = []
    for t in teams_resp["data"]:
        team = Team()
        team.id = t["id"]
        team.name = t["fullName"]
        team.abbreviation = t["rawTricode"]
        if t["franchiseId"]:
            team.franchise = Franchise.objects.get(id=t["franchiseId"])
        teams.append(team)
    Team.objects.bulk_create(teams, ignore_conflicts=True)

    print(teams)


@shared_task
def load_seasons():
    seasons_resp = nhlapi.league.get_seasons()
    seasons = []
    for s in seasons_resp["data"]:
        season = Season()
        season.id = s["id"]
        season.formatted_season_id = s["formattedSeasonId"]
        season.start_date = _eastern_iso_to_utc(s["startDate"])
        season.end_date = _eastern_iso_to_utc(s["endDate"])
        season.preseason_start_date = _eastern_iso_to_utc(s["preseasonStartdate"])
        season.regular_season_end_date = _eastern_iso_to_utc(s["regularSeasonEndDate"])
        seasons.append(season)
    Season.objects.bulk_create(seasons, ignore_conflicts=True)

    print(seasons)


@shared_task
def load_games():
    seasons = Season.objects.all()
    season_ids = [s.id for s in seasons]
    load_season_games.map(season_ids).apply_async()


@shared_task
def load_season_games(season_id: int):
    season = Season.objects.get(id=season_id)
    day = season.start_date.date()
    days = []
    while day < season.end_date.date():
        days.append(day)
        day = day + timedelta(days=7)

    load_weeks_games.map(days).apply_async()


@shared_task
def load_weeks_games(day: date):
    schedule = nhlapi.schedule.get_week_schedule(day)
    games = []
    for d in schedule["gameWeek"]:
        for g in d["games"]:
            game = Game()
            game.id = g["id"]
            game.season = Season.objects.get(id=g["season"])
            game.game_type = g["gameType"]
            game.start_time = g["startTimeUTC"]
            try:
                game.away_team = Team.objects.get(id=g["awayTeam"]["id"])
            except Team.DoesNotExist:
                print(g)
            try:
                game.home_team = Team.objects.get(id=g["homeTeam"]["id"])
            except Team.DoesNotExist:
                print(g)
            games.append(game)
    Game.objects.bulk_create(games, ignore_conflicts=True)

    print(games)


@shared_task
def load_games_play_by_play(game_id: str):
    pbp_resp = nhlapi.game.get_game_play_by_play(game_id)

    for p in pbp_resp['plays']:
        print(p)
        event = None

        if p["typeCode"] in nhlapi.game.shot_type_mapping:
            event = Shot()
            if Shot.objects.filter(game_id=game_id, event_id=p["eventId"]).exists():
                event = Shot.objects.get(game_id=game_id, event_id=p["eventId"])
            event.result = nhlapi.game.shot_type_mapping[p["typeCode"]]
            if event.result == "GOAL":
                event.shooter = p["details"]["scoringPlayerId"]
            else:
                event.shooter = p["details"]["shootingPlayerId"]
            if "goalieInNetId" in p["details"]:
                event.goalie = p["details"]["goalieInNetId"]
            if "blockingPlayerId" in p["details"]:
                event.blocking_player = p["details"]["blockingPlayerId"]
        elif p["typeCode"] == 502:
            event = Faceoff()
            if Faceoff.objects.filter(game_id=game_id, event_id=p["eventId"]).exists():
                event = Faceoff.objects.get(game_id=game_id, event_id=p["eventId"])
            event.winner = p["details"]["winningPlayerId"]
            event.loser = p["details"]["losingPlayerId"]

        if event:
            event.game_id = game_id
            event.event_id = p["eventId"]
            event.period = p["periodDescriptor"]["number"]
            event.time_elapsed = _scoreboard_time_to_seconds(p["timeInPeriod"])
            event.time_remaining = _scoreboard_time_to_seconds(p["timeRemaining"])
            event.save()
