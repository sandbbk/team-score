from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework import (status, viewsets)

from team.serializers import *


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()

    # def put(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(request.data, )
    #     # serializer.is_valid(raise_exception=False)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_200_OK)
