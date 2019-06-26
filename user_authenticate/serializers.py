import hashlib
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from rest_framework.serializers import (ModelSerializer, ReadOnlyField)
from user_authenticate.models import (User, Key)
from user_authenticate.extentions import (send_mail, is_zombie)
from team import (serializers, models)


class UserSerializer(ModelSerializer):
    player = serializers.PlayerSerializer(allow_null=True, default=None)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'img', 'date_joined', 'phone', 'password', 'birthDate', 'player')
        write_only_fields = ('password',)
        read_only_fields = ('date_joined', 'is_admin', 'is_staff', 'is_active')


    @transaction.atomic()
    def create(self, attrs):
        """
            Call set_password on user object. Without this
            the password will be stored in plain text.
        """
        #  Check if user already exists.
        try:
            _user = User.objects.get(email=attrs['email'])
            if is_zombie(_user):
                _user.delete()
            else:
                raise User.IntegrityError(f"User with email {attrs['email']} already exists.")
        except User.DoesNotExist:
            pass

        user = super(UserSerializer, self).create(attrs)
        user.set_password(attrs['password'])
        user.is_active = False
        user.save()

        #  Generates and saves key for link in email.

        key = (hashlib.sha256(user.email.encode('utf-8'))).hexdigest()
        key = Key.objects.create(user=user, data=key, expire_time=(timezone.now() + timedelta(minutes=30)))

        # Send an email to user with link for activation.

        subject = 'Activation of Team-Score account.'
        send_mail(user.email, subject, 'user_authenticate/activate.html', key.data)

        return user

    def update(self, instance, validated_data):
        player = None
        try:
            player = validated_data.pop('player')
        except KeyError:
            pass

        user = super(UserSerializer, self).update(instance, validated_data)
        try:
            password = validated_data['password']
            user.set_password(password)
        except KeyError:
            pass
        user.save()

        if player is not None:
            models.Player.objects.update_or_create(user=user, defaults=player)

        return user

