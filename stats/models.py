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


class Game(models.Model):
    id = models.IntegerField(primary_key=True)
    start_time = models.DateTimeField()
    season = models.CharField(max_length=8)
    game_type = models.SmallIntegerField()
