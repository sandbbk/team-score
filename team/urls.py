from django.urls import (path, re_path, include)
from team.views import (TeamViewSet,)
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

urlpatterns = [
    path('', include(router.urls)),
    # path('teams/<int:pk>/', TeamDetail.as_view()),
]
