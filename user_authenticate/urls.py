from django.urls import path, re_path
from user_authenticate.views import (CreateUserAPIView, authenticate_user, UserDetailAPIView, activate)


urlpatterns = [
    path('create/', CreateUserAPIView.as_view()),
    path('token/', authenticate_user),
    re_path('detail/', UserDetailAPIView.as_view()),
    re_path('^activate/(?P<link>[-a-z0-9]+)$', activate),

]
