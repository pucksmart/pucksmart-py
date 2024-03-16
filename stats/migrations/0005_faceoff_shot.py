# Generated by Django 5.0.2 on 2024-03-16 03:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stats", "0004_game_away_team_game_home_team_alter_game_season"),
    ]

    operations = [
        migrations.CreateModel(
            name="Faceoff",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("event_id", models.IntegerField()),
                ("period", models.SmallIntegerField()),
                ("time_elapsed", models.IntegerField()),
                ("time_remaining", models.IntegerField()),
                ("winner", models.IntegerField()),
                ("loser", models.IntegerField()),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING, to="stats.game"
                    ),
                ),
            ],
            options={
                "abstract": False,
                "unique_together": {("game", "event_id")},
            },
        ),
        migrations.CreateModel(
            name="Shot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("event_id", models.IntegerField()),
                ("period", models.SmallIntegerField()),
                ("time_elapsed", models.IntegerField()),
                ("time_remaining", models.IntegerField()),
                (
                    "result",
                    models.CharField(
                        choices=[
                            ("SOG", "Shot on goal"),
                            ("BLK", "Blocked shot"),
                            ("MISS", "Missed shot"),
                            ("GOAL", "Goal"),
                        ],
                        max_length=4,
                    ),
                ),
                ("shooter", models.IntegerField()),
                ("goalie", models.IntegerField(blank=True, null=True)),
                ("blocking_player", models.IntegerField(blank=True, null=True)),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING, to="stats.game"
                    ),
                ),
            ],
            options={
                "abstract": False,
                "unique_together": {("game", "event_id")},
            },
        ),
    ]
