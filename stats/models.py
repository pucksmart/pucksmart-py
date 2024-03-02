from django.db import models

# Create your models here.


class Franchise(models.Model):
    id = models.IntegerField(primary_key=True)
    full_name = models.CharField(max_length=64)
    common_name = models.CharField(max_length=64)
    place_name = models.CharField(max_length=64)


class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    abbreviation = models.CharField(max_length=3)
    franchise = models.ForeignKey(Franchise, on_delete=models.DO_NOTHING)


class Season(models.Model):
    id = models.IntegerField(primary_key=True)
    formatted_season_id = models.CharField(max_length=7)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    preseason_start_date = models.DateTimeField(null=True, blank=True)
    regular_season_end_date = models.DateTimeField()


class Game(models.Model):
    id = models.IntegerField(primary_key=True)
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    game_type = models.SmallIntegerField()
    start_time = models.DateTimeField()
    away_team = models.ForeignKey(
        Team,
        on_delete=models.DO_NOTHING,
        related_name="games_as_away_team",
        null=True,
        blank=True,
    )
    home_team = models.ForeignKey(
        Team,
        on_delete=models.DO_NOTHING,
        related_name="games_as_home_team",
        null=True,
        blank=True,
    )
