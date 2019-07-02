from rest_framework.serializers import ModelSerializer
from team.models import *
#from user_authenticate.serializers import UserSerializer


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
        fields = ('id', 'event', 'author', 'assistant', 'scoringTeam', 'time', 'condition')


class CardSerializer(ModelSerializer):

    class Meta:
        model = Card
        fields = ('id', 'event', 'author', 'receivedTeam', 'time', 'color')


class SubstitutionSerializer(ModelSerializer):

    class Meta:
        model = Substitution
        fields = ('id', 'event', 'playerIn', 'playerOut', 'inTeam', 'time')


class EventSerializer(ModelSerializer):

    class Meta:

        model = Event
        fields = ('id', 'competition', 'typeOfEvent', 'date', 'startTime', 'status', 'teamA', 'teamB', 'field',
                  'goals', 'cards', 'substitutions')


class RetrieveEventSerializer(ModelSerializer):

    goals = GoalSerializer(many=True)
    cards = CardSerializer(many=True)
    substitutions = SubstitutionSerializer(many=True)

    class Meta:

        model = Event
        fields = ('id', 'competition', 'typeOfEvent', 'date', 'startTime', 'status', 'teamA', 'teamB', 'field',
                  'goals', 'cards', 'substitutions')
        depth = 1
