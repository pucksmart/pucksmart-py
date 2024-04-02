from django.contrib import admin

from stats.models import Franchise, Game, Team

# Register your models here.


@admin.register(Franchise)
class FranchiseAdmin(admin.ModelAdmin):
    list_display = ["id", "full_name"]
    ordering = ["full_name"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "abbreviation"]
    ordering = ["name"]


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ["id", "season", "game_type"]
    ordering = ["id"]
