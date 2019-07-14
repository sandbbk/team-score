from django.urls import (path, re_path, include)
from team.views import (TeamViewSet, EventViewSet)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='teams')
router.register(r'events', EventViewSet, basename='events')

urlpatterns = [
    path('', include(router.urls)),

]
