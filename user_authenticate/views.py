import jwt

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import (RetrieveUpdateDestroyAPIView, ListAPIView, ListCreateAPIView)

from user_authenticate.serializers import UserSerializer
from user_authenticate.models import (User, Key)
from user_authenticate.extentions import key_expired


class UserCreate(APIView):
    # Allow any user (authenticated or not) to access this url
    permission_classes = (permissions.AllowAny,)

    def post(self, request):

        data = request.data
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        serializer.data.pop('password')
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserDetail(RetrieveUpdateDestroyAPIView):
    # Allow only authenticated users to access this url
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        img = None
        try:
            img = request.FILES['img']
        except KeyError:
            pass

        if img:
            serializer_data = {'img': img}
        else:
            serializer_data = request.data

        serializer = UserSerializer(request.user, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserList(ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)


@api_view(['POST'])
@permission_classes([permissions.AllowAny, ])
def authenticate_user(request):
    try:
        email = request.data['email']
        password = request.data['password']

        user = User.objects.get(email=email)
        if not check_password(password, user.password):
            raise KeyError
    except KeyError:
        res = {'error': 'Wrong password'}
        return Response(res, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        res = {'error': 'Wrong email'}
        return Response(res, status=status.HTTP_403_FORBIDDEN)

    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER

    try:
        payload = jwt_payload_handler(user)
        token = jwt.encode(payload, settings.SECRET_KEY)

        user_details = dict()
        user_details['name'] = "%s" % user.email
        user_details['token'] = token

        # send signal when logged in for future.
        user_logged_in.send(sender=user.__class__, request=request, user=user)

        return Response(user_details, status=status.HTTP_200_OK)

    except Exception as e:
        res = {'error': repr(e)}
        return Response(res, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny, ])
def activate(request, link):
    try:
        expired, key = key_expired(link)
        if expired:
            key.user.delete()
            raise KeyError('Time for activation expired!')

        #  Activate of user
        key.user.is_active = True
        key.user.save()
        key.delete()
        response = {'msg': f'{key.user} profile activated.'}

    except Key.DoesNotExist:
        response = {'msg': 'Error: invalid link!'}
    except Exception as e:
        response = {'msg': f'Error: {repr(e)}'}
    return Response(response, status=status.HTTP_400_BAD_REQUEST)



