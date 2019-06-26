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
