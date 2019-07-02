from django.urls import (path, re_path, include)
from team.views import (TeamViewSet, EventViewSet)
from rest_framework.routers import DefaultRouter


# teamList = TeamViewSet.as_view(
#     {
#         'get': 'list', 'post': 'create'
#     })
# teamDetail = TeamViewSet.as_view(
#     {
#         'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
#      })
router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='teams')
router.register(r'events', EventViewSet, basename='events')

urlpatterns = [
    path('', include(router.urls)),
    # path('teams/<int:pk>/', TeamDetail.as_view()),
]
