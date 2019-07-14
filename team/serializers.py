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

    # goals = GoalSerializer(many=True)
    # cards = CardSerializer(many=True)
    # substitutions = SubstitutionSerializer(many=True)

    class Meta:
        model = Event

        fields = ('id', 'competition', 'typeOfEvent', 'date', 'startTime', 'status', 'teamA', 'teamB', 'field',
                  'goals', 'cards', 'substitutions')

    def create(self, validated_data):
        """
            Create Event object with pop out from validated data elements
            like Goals, Cards, Substitutions and create them apart after Event.
        """

        objs = {'goals': Goal, 'cards': Card, 'substitutions': Substitution}
        for k in objs.keys():
            setattr(self, k, validated_data.pop(k))

        event = super(EventSerializer, self).create(validated_data)
        event.save()

        # Optimized db requests with bulk_create. One request per model.

        for k, v in objs.items():
            batch_list = []
            atr = getattr(self, k)
            for item in atr:
                item.update(event=event)
               # v.objects.create(**item)
                batch_list.append(item)
            v.objects.bulk_create(batch_list)

        return event

    def update(self, instance, validated_data):
        """
            Pop  'goals', 'cards', 'substitutions' from serializer's validated_data,
            to create it apart after Event.
        """

        objs = ('goals', 'cards', 'substitutions')
        for item in objs:
            try:
                obj = validated_data.pop(item)
                for element in obj:
                    element.update(event=instance)
                setattr(self, item, obj)
            except KeyError:
                pass

        event = super(EventSerializer, self).update(instance, validated_data)
        event.save()

        for goal in self.goals:
            id_ = goal.pop('id', None)
            if id_:
                Goal.objects.update_or_create(id=id_, defaults=goal)

        # for card in self.cards:
        #     id_ = card.pop('id')
        #     Card.objects.update_or_create(id=id_, defaults=card)
        #
        # for substitution in self.substitutions:
        #     id_ = substitution.pop('id')
        #     Substitution.objects.update_or_create(id=id_, defaults=substitution)
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
