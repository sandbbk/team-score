from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import (status, viewsets, permissions)

from team.serializers import *
from team.models import (Team, Player)
from user_authenticate.permissions import (HasPlayerProfile, IsTeamAdminOrReadOnly, IsEventAdminOrReadOnly)
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

    permission_classes = (permissions.IsAuthenticated, HasPlayerProfile, IsEventAdminOrReadOnly)

    def make_serializer(self, request, obj=None):
        if obj is not None:
            serializer = self.get_serializer(obj, data=request.data, partial=True)
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return serializer

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):

        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        self.check_object_permissions(request, event)

        return Response(self.make_serializer(request, obj=event).data, status=status.HTTP_205_RESET_CONTENT)

    def retrieve(self, request, *args, **kwargs):

        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        serializer = self.get_serializer(event)

        total_data = {}
        total_data.update(serializer.data)
        total_data.update(event.stat)

        return Response(data=total_data, status=status.HTTP_200_OK)
