from django.urls import path, re_path
from user_authenticate.views import (UserCreate, authenticate_user, UserDetail, UserList, activate)


urlpatterns = [
    path('create/', UserCreate.as_view()),
    path('token/', authenticate_user),
    path('detail/', UserDetail.as_view()),
    re_path('^activate/(?P<link>[-a-z0-9]+)$', activate),
    path('list/', UserList.as_view()),
]
