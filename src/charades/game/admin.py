from django.contrib import admin

from charades.game.models import GameSession
from charades.game.models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = [
        "phone_number",
        "is_active",
        "opted_in_at",
        "created_at",
    ]
    list_filter = [
        "is_active",
    ]
    search_fields = [
        "phone_number",
    ]
    readonly_fields = [
        "created_at",
        "opted_in_at",
        "opted_out_at",
    ]


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = [
        "player",
        "word",
        "status",
        "score",
        "started_at",
    ]
    list_filter = [
        "status",
    ]
    search_fields = [
        "player__phone_number",
        "word__text",
    ]
    readonly_fields = [
        "started_at",
        "completed_at",
    ]
