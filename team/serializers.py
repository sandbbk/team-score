from django.db import (transaction, IntegrityError)
from rest_framework.serializers import ModelSerializer
from team.models import *


class CompetitionSerializer(ModelSerializer):

    class Meta:
        model = Competition
        fields = ('id', 'name', 'startDate', 'endDate')


class UseFieldSerializer(ModelSerializer):

    class Meta:
        model = Field
        fields = ('id', 'name', 'city', 'district')


class FieldSerializer(ModelSerializer):

    uses = UseFieldSerializer(many=True, read_only=True)

    class Meta:
        model = Field
        fields = ('id', 'name', 'city', 'district')


class PlayerSerializer(ModelSerializer):

    class Meta:
        model = Player
        read_only_fields = ('teams',)
        fields = ('id', 'role', 'healthStatus', 'number', 'city', 'district', 'teams')


class RetrieveTeamSerializer(ModelSerializer):

    players = PlayerSerializer(many=True)

    class Meta:

        model = Team
        fields = ('id', 'teamName', 'city', 'admin', 'captain', 'favoriteField', 'players')
        depth = 1


class TeamSerializer(ModelSerializer):

    class Meta:

        model = Team
        fields = ('id', 'teamName', 'city', 'admin', 'captain', 'favoriteField', 'players')


class GoalSerializer(ModelSerializer):

    class Meta:
        model = Goal
        fields = ('id', 'author', 'assistant', 'scoringTeam', 'time', 'condition')


class CardSerializer(ModelSerializer):

    class Meta:
        model = Card
        fields = ('id', 'author', 'receivedTeam', 'time', 'color')


class SubstitutionSerializer(ModelSerializer):

    class Meta:
        model = Substitution
        fields = ('id', 'playerIn', 'playerOut', 'inTeam', 'time')


class EventSerializer(ModelSerializer):

    def __init__(self, *args, **kwargs):

        self.nested_id = kwargs.pop('nested_id', False)
        self.objs = {'goals': Goal, 'cards': Card, 'substitutions': Substitution}

        # set parameter 'id' in extra_kwargs to provide update by id.

        if self.nested_id:
            GoalSerializer.Meta.extra_kwargs = {'id': {'read_only': False, 'required': True}}
            CardSerializer.Meta.extra_kwargs = {'id': {'read_only': False, 'required': True}}
            SubstitutionSerializer.Meta.extra_kwargs = {'id': {'read_only': False, 'required': True}}
        super(EventSerializer, self).__init__(*args, **kwargs)

    goals = GoalSerializer(many=True)
    cards = CardSerializer(many=True)
    substitutions = SubstitutionSerializer(many=True)

    class Meta:
        model = Event

        fields = ('id', 'competition', 'typeOfEvent', 'date', 'startTime', 'status', 'teamA', 'teamB', 'field',
                  'goals', 'cards', 'substitutions')

    def set_extra_args(self, validated_data):

        for k in self.objs.keys():
            setattr(self, k, validated_data.pop(k, None))

    def update_or_create_extra_objs(self, obj):

        for k, v in self.objs.items():
            atr = getattr(self, k)

            if atr is None:
                continue
            for item in atr:
                id_ = item.pop('id', None)
                item.update(event=obj)
                v.objects.update_or_create(id=id_, defaults=item)

    @transaction.atomic()
    def create(self, validated_data):
        """
            Create Event object with pop out from validated data elements
            like Goals, Cards, Substitutions and create them apart after Event.
        """

        self.set_extra_args(validated_data)

        # Check when player in both teams, then raise exception.

        def val_from_dict(iterable):
            out = []
            for item in iterable:
                out.extend(item.values())
            return out

        players_A = val_from_dict(validated_data.get('teamA').players.values('id'))
        players_B = val_from_dict(validated_data.get('teamB').players.values('id'))

        def get_matched_ids(a,b):
            matched_ids = []
            for id in players_A:
                if id in players_B:
                    matched_ids.append(id)
            return matched_ids

        matched = get_matched_ids(players_A, players_B)

        if matched:
            raise IntegrityError(f'Players with ids {matched} are in both teams')
        event = super(EventSerializer, self).create(validated_data)
        event.save()

        # creating objs.

        self.update_or_create_extra_objs(event)
        return event

    @transaction.atomic()
    def update(self, instance, validated_data):
        """
            Pop  'goals', 'cards', 'substitutions' from serializer's validated_data,
            to create or update it apart after Event.
        """

        self.set_extra_args(validated_data)

        event = super(EventSerializer, self).update(instance, validated_data)
        event.save()

        self.update_or_create_extra_objs(instance)
        return event


class RetrieveEventSerializer(ModelSerializer):

    goals = GoalSerializer(many=True)
    cards = CardSerializer(many=True)
    substitutions = SubstitutionSerializer(many=True)

    class Meta:

        model = Event
        fields = ('id', 'competition', 'typeOfEvent', 'date', 'startTime', 'status', 'teamA', 'teamB', 'field',
                  'goals', 'cards', 'substitutions')
        depth = 1
