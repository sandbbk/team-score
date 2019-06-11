from django.contrib import admin
from team.models import *


class CompetitionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Competition._meta.fields]


class FieldAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Field._meta.fields]


class UseFieldAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UseField._meta.fields]


class TeamAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Team._meta.fields]


class PlayerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Player._meta.fields]


class EventAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Event._meta.fields]


class GoalAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Goal._meta.fields]


class CardAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Card._meta.fields]


class SubstitutionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Substitution._meta.fields]


admin.site.register(Competition, CompetitionAdmin)

admin.site.register(Field, FieldAdmin)

admin.site.register(UseField, UseFieldAdmin)

admin.site.register(Team, TeamAdmin)

admin.site.register(Player, PlayerAdmin)

admin.site.register(Event, EventAdmin)

admin.site.register(Goal, GoalAdmin)

admin.site.register(Card, CardAdmin)

admin.site.register(Substitution, SubstitutionAdmin)
