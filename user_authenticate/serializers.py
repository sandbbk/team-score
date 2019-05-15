import hashlib
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from rest_framework.serializers import (ModelSerializer, ReadOnlyField)
from user_authenticate.models import (User, Key)
from user_authenticate.extentions import send_mail


class UserSerializer(ModelSerializer):
    date_joined = ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined', 'phone', 'password')
        write_only_fields = ('password',)
        read_only_fields = ('email', 'date_joined', 'is_admin', 'is_staff', 'is_active')

    @transaction.atomic()
    def create(self, attrs):
        """
            Call set_password on user object. Without this
            the password will be stored in plain text.
        """
        user = super(UserSerializer, self).create(attrs)
        user.set_password(attrs['password'])
        user.is_active = False
        user.save()

        #  Generates and saves a key for link in the email.

        key = (hashlib.sha256(user.email.encode('utf-8'))).hexdigest()
        key = Key.objects.create(user=user, data=key, expire_time=(timezone.now() + timedelta(minutes=1)))

        # Send an email to user with link for activation.

        subject = 'Activation of Team-Score account.'
        send_mail(user.email, subject, 'user_authenticate/activate.html', key.data)
        return user

    def update(self, instance, validated_data):
        user = super(UserSerializer, self).update(instance, validated_data)
        try:
            password = validated_data['password']
            user.set_password(password)
        except KeyError:
            pass
        user.save()
        return user
