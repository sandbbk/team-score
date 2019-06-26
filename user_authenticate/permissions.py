from rest_framework.permissions import (BasePermission, SAFE_METHODS)

from team.models import (Player, Team)


class HasPlayerProfile(BasePermission):
    """
        Allows access if user has
        player profile only.
    """

    def has_permission(self, request, view):

        return Player.objects.filter(user=request.user).exists()


class HasUserNecessaryFields(BasePermission):
    """
        Allows access with filled necessary user fields.
    """

    def has_permission(self, request, view):

        return bool(request.uaser.name and request.user)


class IsTeamAdminOrReadOnly(BasePermission):
    """
        Allows extra operations with team to TeamAdmin only.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.admin
