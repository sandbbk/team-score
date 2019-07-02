from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import (status, viewsets, permissions)

from team.serializers import *
from team.models import Team
from user_authenticate.permissions import (HasPlayerProfile, IsTeamAdminOrReadOnly)
from user_authenticate.extentions import cap_to_player


class TeamViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, HasPlayerProfile, IsTeamAdminOrReadOnly)

    def get_queryset(self):

        queryset = Team.objects.all()

        player = Player.objects.get(user=self.request.user)
        teams = self.request.query_params.get('teams')

        if teams == "my":
            queryset = player.team_set.all()
        return queryset

    def get_serializer_class(self):

        if self.action == 'retrieve':
            return RetrieveTeamSerializer
        return TeamSerializer

    def create(self, request, *args, **kwargs):

        data = cap_to_player(request)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):

        team = get_object_or_404(Team, pk=self.kwargs['pk'])
        self.check_object_permissions(request, team)

        serializer = self.get_serializer(team, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, HasPlayerProfile)

    def get_queryset(self):

        queryset = Event.objects.all()
        user = self.request.user
        player = Player.objects.get(user=user)
        events = self.request.query_params.get('events')

        if events == "my":
            queryset = queryset.filter(teamA__players=player) | queryset.filter(teamB__players=player)\
                       | queryset.filter(teamA__admin=user) | queryset.filter(teamB__admin=user)
        return queryset

    def get_serializer_class(self):

        if self.action in ('retrieve', 'list'):
            return RetrieveEventSerializer
        return EventSerializer

    def update(self, request, *args, **kwargs):

        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        #self.check_object_permissions(request, event)

        extra_event = {}
        goals = request.data.pop('goals')
        cards = request.data.pop('cards')
        substitutions = request.data.pop('substitutions')
        extra_event.update(goals=goals, cards=cards, substitutions=substitutions)


        serializer = self.get_serializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)